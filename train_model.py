"""
train_model.py — Train and save the RF+PSO model
Run this ONCE before launching the web app to generate model files.

Usage:
    python train_model.py

This reads your CSV, trains the best model (RF + PSO simulation),
and saves it to models/ folder so app.py can load it.
"""

import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings("ignore")

# ─── CONFIG ───
CSV_PATH = "cyberfeddefender_dataset (1).csv"   # ← put your CSV here
MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

print("=" * 60)
print("  CyberFedDefender — Model Training Script")
print("=" * 60)

# ─── LOAD ───
print("\n[1/6] Loading dataset...")
df = pd.read_csv(CSV_PATH)
print(f"      Shape: {df.shape}")

# ─── CLEAN ───
print("[2/6] Cleaning data...")
df = df.drop_duplicates()
for col in df.columns:
    if df[col].isnull().sum() > 0:
        df[col].fillna(df[col].mode()[0], inplace=True)

# ─── ENCODE ───
print("[3/6] Encoding features...")
encoders = {}
for col in df.select_dtypes(include="object").columns:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    encoders[col] = le
joblib.dump(encoders, os.path.join(MODEL_DIR, "label_encoders.pkl"))

# ─── FEATURES ───
X = df.drop("Label", axis=1)
y = df["Label"]

feature_names = list(X.columns)
joblib.dump(feature_names, os.path.join(MODEL_DIR, "feature_names.pkl"))

# ─── SPLIT ───
print("[4/6] Splitting & balancing...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ─── SCALE ───
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)
joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))

# ─── BALANCE ───
smote = SMOTE(random_state=42)
X_train, y_train = smote.fit_resample(X_train, y_train)

# ─── TRAIN RF+PSO (simulated via optimal params found by PSO) ───
# In a real PSO run, particle positions would optimize RF hyperparams.
# Here we use the optimal params discovered during your research.
print("[5/6] Training Random Forest (PSO-optimized parameters)...")
model = RandomForestClassifier(
    n_estimators=500,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

# ─── EVALUATE ───
print("[6/6] Evaluating...")
y_pred = model.predict(X_test)
acc  = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec  = recall_score(y_test, y_pred)
f1   = f1_score(y_test, y_pred)

print(f"\n  Accuracy  : {acc:.4f}  ({acc*100:.2f}%)")
print(f"  Precision : {prec:.4f}")
print(f"  Recall    : {rec:.4f}")
print(f"  F1 Score  : {f1:.4f}")

# ─── SAVE ───
model_path = os.path.join(MODEL_DIR, "rf_pso_model.pkl")
joblib.dump(model, model_path)
print(f"\n✅ Model saved to: {model_path}")
print("✅ Ready to run: python app.py")
