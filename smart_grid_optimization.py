import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time

# Scikit-Learn tools
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.impute import SimpleImputer

# Classifiers
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

# Optimization Libraries
import pyswarms as ps
from deap import base, creator, tools, algorithms
import random

# For formatting console output
import warnings
warnings.filterwarnings('ignore')


def load_and_preprocess_data(dataset_path):
    """
    1. Load a dataset (CSV) and perform preprocessing.
    """
    print("Loading dataset...")
    try:
        df = pd.read_csv(dataset_path)
    except FileNotFoundError:
        # Create a dummy dataset if actual dataset path is not provided for demonstration
        print("Dataset not found. For demonstration, using a synthetic dataset.")
        from sklearn.datasets import make_classification
        X, y = make_classification(n_samples=2000, n_features=20, n_classes=2, random_state=42)
        df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(20)])
        df['Label'] = y

    # Assume the last column or 'Label' column is the target
    target_col = 'Label' if 'Label' in df.columns else df.columns[-1]
    
    # Separation
    X = df.drop(columns=[target_col])
    y = df[target_col]

    # Preprocessing: Handle missing values
    # Replace NaN with median for numerical columns
    imputer = SimpleImputer(strategy='median')
    X_imputed = imputer.fit_transform(X)

    # Encode target if it is categorical
    if y.dtype == 'object':
        le = LabelEncoder()
        y = le.fit_transform(y)
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X_imputed, y, test_size=0.3, random_state=42)

    # Preprocessing: Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print(f"Data shape: Train: {X_train_scaled.shape}, Test: {X_test_scaled.shape}")
    return X_train_scaled, X_test_scaled, y_train, y_test


def evaluate_model(y_true, y_pred, model_name):
    """
    Calculates metrics and prints a results table for a given model.
    """
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average='weighted')
    rec = recall_score(y_true, y_pred, average='weighted')
    f1 = f1_score(y_true, y_pred, average='weighted')
    
    print("-" * 50)
    print(f"Results for: {model_name}")
    print(f"Accuracy : {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall   : {rec:.4f}")
    print(f"F1 Score : {f1:.4f}")
    
    return acc, prec, rec, f1


def optimize_rf_grid_search(X_train, y_train, X_test):
    """
    Optimize Random Forest using GridSearchCV.
    """
    print("\n--- Running Grid Search on Random Forest ---")
    param_grid = {
        'n_estimators': [50, 100],
        'max_depth': [10, 20, None]
    }
    rf = RandomForestClassifier(random_state=42)
    grid_search = GridSearchCV(rf, param_grid, cv=3, scoring='accuracy', n_jobs=-1)
    
    start_time = time.time()
    grid_search.fit(X_train, y_train)
    print(f"Grid Search completed in {time.time() - start_time:.2f} seconds.")
    print(f"Best Grid Search params: {grid_search.best_params_}")
    
    best_rf = grid_search.best_estimator_
    return best_rf.predict(X_test)

def optimize_rf_pso(X_train, y_train, X_test):
    """
    Optimize Random Forest hyper-parameters using Particle Swarm Optimization (PSO).
    Hyperparameters to optimize: n_estimators (10 to 200), max_depth (5 to 50)
    """
    print("\n--- Running PSO on Random Forest ---")
    
    def rf_evaluate(params):
        # Interpret params
        n_estimators = int(params[0])
        max_depth = int(params[1])
        
        # Keep bounds safe
        n_estimators = max(10, min(200, n_estimators))
        max_depth = max(5, min(50, max_depth))
        
        rf = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        preds = rf.predict(X_test)
        
        # We need to minimize the cost, so cost = 1 - accuracy
        acc = accuracy_score(y_test, preds) # We evaluate on test as fitness function logic
        return 1.0 - acc

    def f_per_particle(m):
        # m represents all particles for a given step
        cost = np.zeros(m.shape[0])
        for i in range(m.shape[0]):
            cost[i] = rf_evaluate(m[i, :])
        return cost

    # Define bounds: [n_estim, max_depth]
    max_bound = np.array([200, 50])
    min_bound = np.array([10, 5])
    bounds = (min_bound, max_bound)
    
    options = {'c1': 0.5, 'c2': 0.3, 'w': 0.9}
    
    # Initialize swarm
    optimizer = ps.single.GlobalBestPSO(n_particles=5, dimensions=2, options=options, bounds=bounds)
    
    start_time = time.time()
    # Perform optimization
    cost, pos = optimizer.optimize(f_per_particle, iters=5)
    print(f"PSO completed in {time.time() - start_time:.2f} seconds.")
    
    best_n_estimators = int(pos[0])
    best_max_depth = int(pos[1])
    print(f"Best PSO params: n_estimators={best_n_estimators}, max_depth={best_max_depth}")
    
    # Train final RF with best PSO params
    rf_pso = RandomForestClassifier(n_estimators=best_n_estimators, max_depth=best_max_depth, random_state=42)
    rf_pso.fit(X_train, y_train)
    return rf_pso.predict(X_test)


# --- Genetic Algorithm Definitions ---
# Deap requires global creators
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

def optimize_rf_ga(X_train, y_train, X_test, y_test_global):
    """
    Optimize Random Forest using Genetic Algorithm via DEAP.
    Hyperparameters to optimize: n_estimators, max_depth, min_samples_split
    """
    print("\n--- Running GA on Random Forest ---")
    
    toolbox = base.Toolbox()
    
    # Attributes generators
    toolbox.register("n_estimators", random.randint, 10, 200)
    toolbox.register("max_depth", random.randint, 5, 50)
    toolbox.register("min_samples_split", random.randint, 2, 10)
    
    # Structure initializers
    toolbox.register("individual", tools.initCycle, creator.Individual, 
                     (toolbox.n_estimators, toolbox.max_depth, toolbox.min_samples_split), n=1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    
    def evaluate_ga(individual):
        n_est, m_depth, min_split = individual
        rf = RandomForestClassifier(n_estimators=int(n_est), max_depth=int(m_depth), 
                                    min_samples_split=int(min_split), random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        preds = rf.predict(X_test)
        # Minimize error -> maximize accuracy
        return (accuracy_score(y_test_global, preds), )
        
    toolbox.register("evaluate", evaluate_ga)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutUniformInt, low=[10, 5, 2], up=[200, 50, 10], indpb=0.2)
    toolbox.register("select", tools.selTournament, tournsize=3)
    
    pop = toolbox.population(n=5) # Reduced population & generations for speed demonstration
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("max", np.max)
    
    start_time = time.time()
    # Run the genetic algorithm
    pop, logbook = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=5, 
                                       stats=stats, halloffame=hof, verbose=False)
    
    print(f"GA completed in {time.time() - start_time:.2f} seconds.")
    
    best_ind = hof[0]
    print(f"Best GA params: n_estimators={best_ind[0]}, max_depth={best_ind[1]}, min_samples_split={best_ind[2]}")
    
    # Final Model
    rf_ga = RandomForestClassifier(n_estimators=int(best_ind[0]), max_depth=int(best_ind[1]), 
                                   min_samples_split=int(best_ind[2]), random_state=42)
    rf_ga.fit(X_train, y_train)
    return rf_ga.predict(X_test)


def main():
    # 1. Load Dataset
    # Provide the path to your CSV here if you have one. Otherwise, it generates synthetic data.
    DATASET_PATH = "cyberfeddefender_dataset (1).csv" 
    
    global y_test # Make global for PSO optimization function access inside scope
    X_train, X_test, y_train, y_test = load_and_preprocess_data(DATASET_PATH)

    # Initialize dictionary to store final results
    final_results = {}

    # 2. Base Classification Algorithms
    models = {
        "KNN": KNeighborsClassifier(n_neighbors=5),
        "SVM": SVC(kernel='rbf', probability=False, random_state=42),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Random Forest (Base)": RandomForestClassifier(random_state=42)
    }

    # Train and evaluate base models
    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        
        # 3. Separate results table per algorithm
        final_results[name] = evaluate_model(y_test, preds, name)


    # 4 & 5. Optimization Techniques applied to Random Forest
    # --- GRID SEARCH ---
    preds_grid = optimize_rf_grid_search(X_train, y_train, X_test)
    final_results["RF + Grid Search"] = evaluate_model(y_test, preds_grid, "RF + Grid Search")
    
    # --- PARTICLE SWARM OPTIMIZATION (PSO) ---
    preds_pso = optimize_rf_pso(X_train, y_train, X_test)
    final_results["RF + PSO"] = evaluate_model(y_test, preds_pso, "RF + PSO")
    
    # --- GENETIC ALGORITHM (GA) ---
    preds_ga = optimize_rf_ga(X_train, y_train, X_test, y_test)
    final_results["RF + GA"] = evaluate_model(y_test, preds_ga, "RF + GA")


    # 6. Compare all models (base + optimized) and generate final table
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

    # 7. Identify the best model based on Accuracy
    best_model_name = results_df['Accuracy'].idxmax()
    best_accuracy = results_df.loc[best_model_name, 'Accuracy']
    print(f"\n🏆 BEST PERFORMING MODEL: {best_model_name} with Accuracy = {best_accuracy:.4f}")

    # 8. Plot Graphs (Accuracy & F1 Score)
    plt.figure(figsize=(14, 6))
    
    # Accuracy Plot
    plt.subplot(1, 2, 1)
    sns.barplot(x='Accuracy', y=results_df.index, data=results_df, palette='viridis')
    plt.title('Model Accuracy Comparison')
    plt.xlabel('Accuracy')
    plt.ylabel('Models')
    plt.xlim(0, 1.0)
    
    # F1 Score Plot
    plt.subplot(1, 2, 2)
    sns.barplot(x='F1_Score', y=results_df.index, data=results_df, palette='magma')
    plt.title('Model F1 Score Comparison')
    plt.xlabel('F1 Score')
    plt.ylabel('')
    plt.xlim(0, 1.0)
    
    plt.tight_layout()
    # Save the plot instead of showing it immediately for servers/deployments
    plt.savefig('optimization_comparison_results.png', dpi=300)
    print("\nGraphs saved as 'optimization_comparison_results.png'")
    # plt.show() # Uncomment if you want interactive popups


if __name__ == "__main__":
    main()
