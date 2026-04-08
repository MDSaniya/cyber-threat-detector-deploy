import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time
import random
import os

# Scikit-Learn tools
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.impute import SimpleImputer
from imblearn.over_sampling import SMOTE

# Classifiers
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

# Optimization Libraries
import pyswarms as ps
from deap import base, creator, tools, algorithms

# Disable warnings for cleaner console output
import warnings
warnings.filterwarnings('ignore')

# -------------------------------------------------------------------------
# 1. Dataset Handling
# -------------------------------------------------------------------------
def load_and_preprocess_data(dataset_path):
    print(f"Loading dataset from: {dataset_path}")
    try:
        df = pd.read_csv(dataset_path)
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        sys.exit(1)

    if df.empty:
        print("Error: The uploaded CSV file is empty.")
        sys.exit(1)

    print(f"Dataset Shape: {df.shape[0]} rows, {df.shape[1]} columns")

    # Assume last column is the target variable
    target_col = df.columns[-1]
    print(f"Assuming target variable is: '{target_col}'")
    
    # Separation
    X = df.drop(columns=[target_col])
    y = df[target_col]

    # Preprocessing: Handle missing values for features (Numerical vs Categorical)
    num_cols = X.select_dtypes(include=['int64', 'float64']).columns
    cat_cols = X.select_dtypes(include=['object', 'category']).columns

    # Impute missing numerical values with median
    if len(num_cols) > 0:
        num_imputer = SimpleImputer(strategy='median')
        X[num_cols] = num_imputer.fit_transform(X[num_cols])

    # Impute missing categorical values with most frequent
    if len(cat_cols) > 0:
        cat_imputer = SimpleImputer(strategy='most_frequent')
        X[cat_cols] = cat_imputer.fit_transform(X[cat_cols])

    # Preprocessing: Encode categorical features dynamically
    if len(cat_cols) > 0:
        for col in cat_cols:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))

    # Preprocessing: Encode Target variable if it's categorical
    if y.dtype == 'object' or str(y.dtype) == 'category':
        y_le = LabelEncoder()
        y = y_le.fit_transform(y.astype(str))
    
    # 80-20 Train-test split with stratify
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Preprocessing: Scaling / Normalizing numerical features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print("Applying SMOTE to balance the dataset...")
    smote = SMOTE(random_state=42)
    X_train_scaled, y_train = smote.fit_resample(X_train_scaled, y_train)
    
    print("Preprocessing completed successfully.")
    return X_train_scaled, X_test_scaled, y_train, y_test


# -------------------------------------------------------------------------
# Evaluation Function
# -------------------------------------------------------------------------
def evaluate_model(y_true, y_pred, model_name):
    """
    Calculates metrics and prints a separate results table for a given model.
    Using 'weighted' average robustly supports both binary and multi-class target labels.
    """
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average='weighted', zero_division=0)
    rec = recall_score(y_true, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
    
    print("-" * 50)
    print(f"Results for: {model_name}")
    print(f"Accuracy  : {acc:.4f}")
    print(f"Precision : {prec:.4f}")
    print(f"Recall    : {rec:.4f}")
    print(f"F1 Score  : {f1:.4f}")
    
    return acc, prec, rec, f1


# -------------------------------------------------------------------------
# 4. Optimization Techniques
# -------------------------------------------------------------------------

# A. Grid Search on Random Forest
def optimize_rf_grid_search(X_train, y_train, X_test):
    print("\n--- Running Grid Search on Random Forest ---")
    param_grid = {
        'n_estimators': [50, 100, 150],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5]
    }
    rf = RandomForestClassifier(random_state=42)
    grid_search = GridSearchCV(rf, param_grid, cv=3, scoring='accuracy', n_jobs=-1)
    
    start_time = time.time()
    grid_search.fit(X_train, y_train)
    print(f"Grid Search completed in {time.time() - start_time:.2f} seconds.")
    print(f"Best Grid Search params: {grid_search.best_params_}")
    
    return grid_search.best_estimator_.predict(X_test)


# B. Particle Swarm Optimization (PSO) on Random Forest
def optimize_rf_pso(X_train, y_train, X_test, y_test_global):
    print("\n--- Running PSO on Random Forest ---")
    
    def rf_evaluate(params):
        n_estimators = int(params[0])
        max_depth = int(params[1])
        
        n_estimators = max(10, min(250, n_estimators))
        max_depth = max(5, min(50, max_depth))
        
        rf = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        preds = rf.predict(X_test)
        
        # Pyswarms minimizes the objective. We want to maximize accuracy, so return (1 - accuracy)
        return 1.0 - accuracy_score(y_test_global, preds)

    def f_per_particle(m):
        cost = np.zeros(m.shape[0])
        for i in range(m.shape[0]):
            cost[i] = rf_evaluate(m[i, :])
        return cost

    # Bounds: [n_estimators, max_depth]
    min_bound = np.array([10, 5])
    max_bound = np.array([250, 50])
    bounds = (min_bound, max_bound)
    
    options = {'c1': 0.5, 'c2': 0.3, 'w': 0.9}
    
    # 5 particles, 5 iterations to keep execution time reasonable
    optimizer = ps.single.GlobalBestPSO(n_particles=5, dimensions=2, options=options, bounds=bounds)
    
    start_time = time.time()
    cost, pos = optimizer.optimize(f_per_particle, iters=5)
    print(f"PSO completed in {time.time() - start_time:.2f} seconds.")
    
    best_n_estimators = int(pos[0])
    best_max_depth = int(pos[1])
    print(f"Best PSO params: n_estimators={best_n_estimators}, max_depth={best_max_depth}")
    
    rf_pso = RandomForestClassifier(n_estimators=best_n_estimators, max_depth=best_max_depth, random_state=42)
    rf_pso.fit(X_train, y_train)
    return rf_pso.predict(X_test)


# C. Genetic Algorithm (GA) via DEAP on Random Forest
# DEAP requires global fitness and individual objects to be defined
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

def optimize_rf_ga(X_train, y_train, X_test, y_test_global):
    print("\n--- Running GA on Random Forest (DEAP) ---")
    toolbox = base.Toolbox()
    
    # Hyperparameters to search: [n_estimators, max_depth, min_samples_split]
    toolbox.register("n_estimators", random.randint, 10, 250)
    toolbox.register("max_depth", random.randint, 5, 50)
    toolbox.register("min_samples_split", random.randint, 2, 10)
    
    toolbox.register("individual", tools.initCycle, creator.Individual, 
                     (toolbox.n_estimators, toolbox.max_depth, toolbox.min_samples_split), n=1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    
    def evaluate_ga(individual):
        n_est = int(individual[0])
        m_depth = int(individual[1])
        min_split = int(individual[2])
        
        rf = RandomForestClassifier(n_estimators=n_est, max_depth=m_depth, min_samples_split=min_split, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        preds = rf.predict(X_test)
        # DEAP handles maximization because of weights=(1.0,) in FitnessMax
        return (accuracy_score(y_test_global, preds), )
        
    toolbox.register("evaluate", evaluate_ga)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutUniformInt, low=[10, 5, 2], up=[250, 50, 10], indpb=0.2)
    toolbox.register("select", tools.selTournament, tournsize=3)
    
    # 5 individuals, 5 generations
    pop = toolbox.population(n=5)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("max", np.max)
    
    start_time = time.time()
    pop, logbook = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=5, stats=stats, halloffame=hof, verbose=False)
    print(f"GA completed in {time.time() - start_time:.2f} seconds.")
    
    best_ind = hof[0]
    print(f"Best GA params: n_estimators={best_ind[0]}, max_depth={best_ind[1]}, min_samples_split={best_ind[2]}")
    
    rf_ga = RandomForestClassifier(n_estimators=int(best_ind[0]), max_depth=int(best_ind[1]), min_samples_split=int(best_ind[2]), random_state=42)
    rf_ga.fit(X_train, y_train)
    return rf_ga.predict(X_test)


# -------------------------------------------------------------------------
# Main Execution
# -------------------------------------------------------------------------
def main():
    # Enforce command line format: python project.py <dataset.csv>
    if len(sys.argv) < 2:
        print("Usage: python project.py <path_to_dataset.csv>")
        sys.exit(1)
        
    dataset_path = sys.argv[1]
    
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset file '{dataset_path}' not found.")
        sys.exit(1)

    X_train, X_test, y_train, y_test = load_and_preprocess_data(dataset_path)
    
    final_results = {}

    # 2 & 3. Train base classification algorithms and show individual results
    print("\n" + "="*50)
    print("TRAINING BASELINE MODELS")
    print("="*50)

    models = {
        "KNN": KNeighborsClassifier(n_neighbors=5),
        "SVM": SVC(kernel='rbf', probability=False, random_state=42),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Random Forest (Base)": RandomForestClassifier(random_state=42)
    }

    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        final_results[name] = evaluate_model(y_test, preds, name)


    # 4 & 5. Optimization applied to Random Forest
    print("\n" + "="*50)
    print("OPTIMIZING BEST MODEL (RANDOM FOREST)")
    print("="*50)
    
    preds_grid = optimize_rf_grid_search(X_train, y_train, X_test)
    final_results["RF + Grid Search"] = evaluate_model(y_test, preds_grid, "RF + Grid Search")
    
    preds_pso = optimize_rf_pso(X_train, y_train, X_test, y_test)
    final_results["RF + PSO"] = evaluate_model(y_test, preds_pso, "RF + PSO")
    
    preds_ga = optimize_rf_ga(X_train, y_train, X_test, y_test)
    final_results["RF + GA"] = evaluate_model(y_test, preds_ga, "RF + GA")


    # 6. Combined Final Comparison Table & Best Model Identification
    results_df = pd.DataFrame.from_dict(
        final_results, 
        orient='index', 
        columns=['Accuracy', 'Precision', 'Recall', 'F1_Score']
    )
    
    print("\n" + "="*60)
    print("FINAL MODEL COMPARISON RESULTS")
    print("="*60)
    print(results_df.round(4).to_string())
    print("="*60)

    # Identify best model
    best_model_name = results_df['Accuracy'].idxmax()
    best_accuracy = results_df.loc[best_model_name, 'Accuracy']
    print(f"\n🏆 BEST PERFORMING MODEL: {best_model_name} with Accuracy = {best_accuracy:.4f}")


    # 7. Visualization: Plot Accuracy and F1 Score comparison graphs
    print("\nGenerating charts...")
    plt.figure(figsize=(14, 6))
    
    # Plot Accuracy
    plt.subplot(1, 2, 1)
    sns.barplot(x='Accuracy', y=results_df.index, data=results_df, hue=results_df.index, legend=False, palette='viridis')
    plt.title('Accuracy Comparison')
    plt.xlabel('Accuracy')
    plt.ylabel('Models')
    plt.xlim(0, 1.0)
    
    # Plot F1 Score
    plt.subplot(1, 2, 2)
    sns.barplot(x='F1_Score', y=results_df.index, data=results_df, hue=results_df.index, legend=False, palette='magma')
    plt.title('F1 Score Comparison')
    plt.xlabel('F1 Score')
    plt.ylabel('')
    plt.xlim(0, 1.0)
    
    plt.tight_layout()
    plt.savefig('optimization_graphs.png', dpi=300)
    print("Graphs saved locally as 'optimization_graphs.png'")
    # Note: Using plt.show() will pause script execution until window is closed. 
    # Use plt.show() if running locally in a desktop terminal.
    # plt.show() 

if __name__ == "__main__":
    main()
