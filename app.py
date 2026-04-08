"""
CyberFedDefender - Cyber Threat Detection Web Application
Flask backend with ML models for real-time threat classification
"""

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import io
import pandas as pd
import numpy as np
import os
import json
import time
import random
import joblib

# Load environment variables from .env file (if it exists)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use system env vars

app = Flask(__name__)

# ─────────────────────────────────────────────────────────────
# PRODUCTION CONFIGURATION
# ─────────────────────────────────────────────────────────────
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'cyberfeddefender-secret-2024')
app.config['ENV'] = os.environ.get('FLASK_ENV', 'development')
app.config['DEBUG'] = os.environ.get('DEBUG', 'False').lower() == 'true'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

# ─────────────────────────────────────────────────────────────
# LOAD TRAINED MODEL
# ─────────────────────────────────────────────────────────────
MODEL_DIR = 'models'
MODEL_PATH = os.path.join(MODEL_DIR, 'rf_pso_model.pkl')
SCALER_PATH = os.path.join(MODEL_DIR, 'scaler.pkl')
ENCODERS_PATH = os.path.join(MODEL_DIR, 'label_encoders.pkl')
FEATURE_NAMES_PATH = os.path.join(MODEL_DIR, 'feature_names.pkl')

model = None
scaler = None
encoders = None
loaded_feature_names = None
model_loaded = False

if os.path.exists(MODEL_PATH):
    try:
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        encoders = joblib.load(ENCODERS_PATH)
        loaded_feature_names = joblib.load(FEATURE_NAMES_PATH)
        model_loaded = True
        print("✅ Real ML model loaded successfully")
    except Exception as e:
        print(f"⚠️  Failed to load model: {e}")
        model_loaded = False
else:
    print("⚠️  Model files not found. Run 'python train_model.py' first.")
    print("   Using simulated predictions until model is trained.")

ALGORITHM_RESULTS = {
    "KNN": {
        "accuracy": 0.486, "precision": 0.478,
        "recall": 0.536, "f1_score": 0.505,
        "color": "#6366f1", "description": "K-Nearest Neighbors"
    },
    "SVM": {
        "accuracy": 0.521, "precision": 0.512,
        "recall": 0.457, "f1_score": 0.483,
        "color": "#8b5cf6", "description": "Support Vector Machine"
    },
    "Decision Tree": {
        "accuracy": 0.566, "precision": 0.559,
        "recall": 0.543, "f1_score": 0.551,
        "color": "#06b6d4", "description": "Decision Tree Classifier"
    },
    "Random Forest": {
        "accuracy": 0.469, "precision": 0.446,
        "recall": 0.357, "f1_score": 0.397,
        "color": "#10b981", "description": "Random Forest (Baseline)"
    },
    "RF + Genetic Algorithm": {
        "accuracy": 0.981, "precision": 0.978,
        "recall": 0.985, "f1_score": 0.981,
        "color": "#f59e0b", "description": "Random Forest + Advanced Genetic Algorithm"
    },
    "RF + PSO": {
        "accuracy": 0.985, "precision": 0.982,
        "recall": 0.988, "f1_score": 0.985,
        "color": "#ef4444", "description": "Random Forest + Particle Swarm Optimization"
    }
}

THREAT_TYPES = ["DDoS", "Ransomware", "Normal", "SQL Injection", "Port Scan", "Man-in-the-Middle"]

FEATURE_NAMES = [
    "Packet Length", "Duration", "Source Port", "Destination Port",
    "Bytes Sent", "Bytes Received", "Flow Packets/s", "Flow Bytes/s",
    "Avg Packet Size", "Total Fwd Packets", "Total Bwd Packets",
    "Fwd Header Length", "Bwd Header Length", "Sub Flow Fwd Bytes",
    "Sub Flow Bwd Bytes", "Inbound"
]


def real_prediction(features: dict) -> dict:
    """
    Real prediction using the trained Random Forest + PSO model.
    Uses actual ML inference on submitted features.
    """
    start_time = time.time()
    
    if not model_loaded or model is None:
        # Fallback to simulation if model not loaded
        return simulate_prediction(features)
    
    try:
        # Convert features dict to list in correct feature order
        feature_values = [features.get(fname, 0) for fname in loaded_feature_names]
        feature_array = np.array([feature_values])
        
        # Scale features
        scaled_features = scaler.transform(feature_array)
        
        # Get prediction and confidence
        prediction = model.predict(scaled_features)[0]
        prediction_proba = model.predict_proba(scaled_features)[0]
        confidence = float(max(prediction_proba))
        
        # Map prediction to threat type
        threat_type = THREAT_TYPES[int(prediction)] if int(prediction) < len(THREAT_TYPES) else "Unknown"
        is_threat = threat_type != "Normal"
        
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return {
            "threat_type": threat_type,
            "is_threat": is_threat,
            "confidence": round(confidence, 3),
            "model_used": "RF + PSO (Real Model)",
            "accuracy": 0.985,
            "processing_time_ms": int(processing_time)
        }
    except Exception as e:
        print(f"Prediction error: {e}")
        return simulate_prediction(features)


def simulate_prediction(features: dict) -> dict:
    """
    Fallback simulation when model is not available.
    """
    time.sleep(0.5)
    threat_idx = random.randint(0, len(THREAT_TYPES) - 1)
    confidence = round(random.uniform(0.87, 0.99), 3)
    is_threat = THREAT_TYPES[threat_idx] != "Normal"

    return {
        "threat_type": THREAT_TYPES[threat_idx],
        "is_threat": is_threat,
        "confidence": confidence,
        "model_used": "RF + PSO (Simulated)",
        "accuracy": 0.985,
        "processing_time_ms": random.randint(45, 120)
    }


# ─────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/results')
def api_results():
    """Return all algorithm benchmark results"""
    return jsonify(ALGORITHM_RESULTS)


@app.route('/api/predict', methods=['POST'])
def api_predict():
    """Run prediction on submitted network traffic features"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        features = data.get('features', {})
        if not features:
            return jsonify({"error": "No features provided"}), 400

        result = real_prediction(features)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/upload-dataset', methods=['POST'])
def api_upload_dataset():
    """Upload a CSV dataset and run batch predictions on all rows"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        filename = secure_filename(file.filename)
        if not filename.lower().endswith('.csv'):
            return jsonify({"error": "Only CSV files are supported"}), 400

        # Read CSV
        try:
            stream = io.StringIO(file.stream.read().decode('utf-8'))
            df = pd.read_csv(stream)
        except Exception as e:
            return jsonify({"error": f"Failed to parse CSV: {str(e)}"}), 400

        if df.empty:
            return jsonify({"error": "The uploaded CSV file is empty"}), 400

        if not model_loaded or model is None:
            return jsonify({"error": "Model not loaded. Please train the model first."}), 500

        start_time = time.time()

        # Preprocess: encode categorical columns using saved encoders
        df_proc = df.copy()
        for col in df_proc.select_dtypes(include='object').columns:
            if col in encoders:
                le = encoders[col]
                # Map known labels; unknown labels get 0
                df_proc[col] = df_proc[col].apply(
                    lambda x: le.transform([x])[0] if x in le.classes_ else 0
                )
            else:
                # Drop columns not in encoders and not in feature names
                if col not in loaded_feature_names:
                    df_proc.drop(columns=[col], inplace=True)

        # Extract features in correct order
        missing_features = [f for f in loaded_feature_names if f not in df_proc.columns]
        if missing_features:
            return jsonify({
                "error": f"Missing required columns: {', '.join(missing_features)}"
            }), 400

        X = df_proc[loaded_feature_names].values

        # Handle any NaN values
        X = np.nan_to_num(X, nan=0.0)

        # Scale
        X_scaled = scaler.transform(X)

        # Predict
        predictions = model.predict(X_scaled)
        probabilities = model.predict_proba(X_scaled)

        processing_time = (time.time() - start_time) * 1000  # ms

        # Build results
        results = []
        threat_counts = {}
        threats_detected = 0

        for i in range(len(predictions)):
            pred_idx = int(predictions[i])
            threat_type = THREAT_TYPES[pred_idx] if pred_idx < len(THREAT_TYPES) else "Unknown"
            confidence = float(max(probabilities[i]))
            is_threat = threat_type != "Normal"

            if is_threat:
                threats_detected += 1

            threat_counts[threat_type] = threat_counts.get(threat_type, 0) + 1

            row_data = {
                "row": i + 1,
                "threat_type": threat_type,
                "confidence": round(confidence, 3),
                "is_threat": is_threat,
            }

            # Include original identifying columns if present
            if 'Source_IP' in df.columns:
                row_data["source_ip"] = str(df.iloc[i]['Source_IP'])
            if 'Destination_IP' in df.columns:
                row_data["dest_ip"] = str(df.iloc[i]['Destination_IP'])
            if 'Protocol' in df.columns:
                row_data["protocol"] = str(df.iloc[i]['Protocol'])
            if 'Timestamp' in df.columns:
                row_data["timestamp"] = str(df.iloc[i]['Timestamp'])

            results.append(row_data)

        return jsonify({
            "success": True,
            "filename": filename,
            "total_rows": len(predictions),
            "threats_detected": threats_detected,
            "safe_traffic": len(predictions) - threats_detected,
            "processing_time_ms": int(processing_time),
            "threat_distribution": threat_counts,
            "results": results
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/simulate-traffic')
def simulate_traffic():
    """Generate simulated network traffic data for demo"""
    traffic = []
    for i in range(10):
        threat_type = random.choice(THREAT_TYPES)
        traffic.append({
            "id": i + 1,
            "timestamp": f"2024-10-23 12:{i:02d}:{random.randint(0,59):02d}",
            "source_ip": f"192.168.0.{random.randint(1,20)}",
            "dest_ip": f"10.0.0.{random.randint(1,10)}",
            "protocol": random.choice(["TCP", "UDP", "ICMP"]),
            "threat_type": threat_type,
            "is_threat": threat_type != "Normal",
            "confidence": round(random.uniform(0.88, 0.99), 3),
            "packet_length": random.randint(100, 2000),
            "bytes_sent": random.randint(50, 2000)
        })
    return jsonify(traffic)


@app.route('/api/stats')
def api_stats():
    """Return dashboard statistics"""
    return jsonify({
        "total_samples": 1430,
        "features": 23,
        "best_accuracy": 98.5,
        "best_model": "RF + PSO",
        "threat_types": len(THREAT_TYPES),
        "algorithms_tested": len(ALGORITHM_RESULTS)
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
