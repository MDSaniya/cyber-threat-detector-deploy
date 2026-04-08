"""
CyberFedDefender - Cyber Threat Detection Web Application
Flask backend with ML models for real-time threat classification
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import os
import json
import time
import random

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

# ─────────────────────────────────────────────────────────────
# SIMULATED MODEL RESULTS (replace with real trained model)
# In production, load your trained model via joblib/pickle
# ─────────────────────────────────────────────────────────────

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


def simulate_prediction(features: dict) -> dict:
    """
    Simulate prediction using the best model (RF + PSO).
    Replace this with your actual trained model inference.
    """
    # Simulate processing time
    time.sleep(0.5)

    # In production: load model and predict
    # model = joblib.load('models/rf_pso_model.pkl')
    # scaler = joblib.load('models/scaler.pkl')
    # scaled = scaler.transform([list(features.values())])
    # prediction = model.predict(scaled)[0]
    # confidence = max(model.predict_proba(scaled)[0])

    # Simulated result
    threat_idx = random.randint(0, len(THREAT_TYPES) - 1)
    confidence = round(random.uniform(0.87, 0.99), 3)
    is_threat = THREAT_TYPES[threat_idx] != "Normal"

    return {
        "threat_type": THREAT_TYPES[threat_idx],
        "is_threat": is_threat,
        "confidence": confidence,
        "model_used": "RF + PSO",
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

        result = simulate_prediction(features)
        return jsonify(result)

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
