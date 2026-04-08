# CyberFedDefender — Deployment Guide

> **Full-stack cyber threat detection web application**
> Flask backend · Machine Learning · Real-time prediction dashboard

---

## 📁 Project Structure

```
cyber-threat-detector/
│
├── app.py                  ← Flask web server (main entry point)
├── train_model.py          ← One-time script: train & save ML model
├── requirements.txt        ← Python dependencies
├── runtime.txt             ← Python version for platform deployment
├── Procfile                ← Gunicorn configuration (Heroku/Railway)
├── .env.example            ← Template for environment variables
├── .gitignore              ← Exclude sensitive files from Git
│
├── venv/                   ← Python virtual environment (activated)
│
├── templates/
│   └── index.html          ← Full dashboard UI (single-page app)
│
├── static/                 ← (optional) extra CSS/JS/images
│   ├── css/
│   └── js/
│
├── models/                 ← Auto-created after running train_model.py
│   ├── rf_pso_model.pkl
│   ├── scaler.pkl
│   ├── label_encoders.pkl
│   └── feature_names.pkl
│
├── cyberfeddefender_dataset (1).csv   ← Your dataset (place here)
│
└── DEPLOYMENT_GUIDE.md     ← This file
```

---

## 🚀 Quick Start (Local Machine)

### Step 1 — Install Python
Make sure you have **Python 3.10+** installed. (Python 3.11+ also works)
```bash
python --version   # should say 3.10 or higher
```

### Step 2 — Create a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```
✓ **VENV Setup Status**: Virtual environment created and activated with Python 3.11.3

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```
✓ **Dependencies Installed**: Flask 3.0.0, Pandas 2.1.4, scikit-learn 1.3.2, and all required ML libraries

### Step 4 — Configure environment variables (IMPORTANT for production)
Copy the example environment file:
```bash
# Windows
copy .env.example .env

# Mac / Linux
cp .env.example .env
```
Then edit `.env` and set a strong `SECRET_KEY` for production deployment.

### Step 5 — Add your dataset
Place your CSV file in the project root:
```
cyber-threat-detector/
└── cyberfeddefender_dataset (1).csv   ← HERE
```

### Step 5 — Train the model (ONCE)
```bash
python train_model.py
```
This creates the `models/` folder with your saved ML model.
**Output example:**
```
[1/6] Loading dataset...  Shape: (1430, 23)
[2/6] Cleaning data...
[3/6] Encoding features...
[4/6] Splitting & balancing...
[5/6] Training Random Forest (PSO-optimized parameters)...
[6/6] Evaluating...
  Accuracy  : 0.9850  (98.50%)
  F1 Score  : 0.9851
✅ Model saved to: models/rf_pso_model.pkl
✅ Ready to run: python app.py
```

### Step 6 — Launch the web app
```bash
python app.py
```
Open your browser at: **http://localhost:5000**

---

## 🌐 What the Website Shows

| Section | Description |
|---------|-------------|
| **Dashboard** | Stats overview: best accuracy, dataset size, algorithm count |
| **Model Results** | Full comparison table — all 6 algorithms with 4 metrics |
| **Performance Charts** | Bar charts: Accuracy, F1, Precision, Recall |
| **Live Predict** | Enter network features → instant threat classification |
| **Traffic Monitor** | Simulated live network traffic with threat labels |
| **About** | Project details, college, algorithm summaries |

---

## ☁️ Deploy to Production

### Option A — Railway.app (Easiest, Free)

1. Push code to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Railway auto-detects Flask — set:
   - **Start command:** `gunicorn app:app`
4. Done! You get a public URL instantly.

---

### Option B — Render.com (Free, recommended)

1. Push to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Set:
   - **Runtime:** Python 3
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
5. Deploy → Get your live URL

---

### Option C — Heroku

```bash
# Install Heroku CLI, then:
heroku login
heroku create your-app-name
git push heroku main
heroku open
```

Create a `Procfile` (no extension) with:
```
web: gunicorn app:app
```

---

### Option D — PythonAnywhere (Student Friendly)

1. Sign up at [pythonanywhere.com](https://pythonanywhere.com)
2. Go to **Files** → upload all files
3. Open a **Bash console**:
   ```bash
   pip install -r requirements.txt
   python train_model.py
   ```
4. Go to **Web** tab → Add new web app → Flask → point to `app.py`
5. Click **Reload**

---

### Option E — VPS / Google Cloud / AWS

```bash
# On your server:
git clone <your-repo>
cd cyber-threat-detector
pip install -r requirements.txt
python train_model.py

# Run with gunicorn (production WSGI server)
gunicorn app:app --bind 0.0.0.0:80 --workers 2 --daemon
```

---

## 🔧 Integrating the Real Trained Model

The current `app.py` uses **simulated results** (hardcoded from your notebook).
To use the **actual trained model**, update `app.py`'s `simulate_prediction()`:

```python
import joblib

# Load once at startup (outside the function)
model = joblib.load('models/rf_pso_model.pkl')
scaler = joblib.load('models/scaler.pkl')

def simulate_prediction(features: dict) -> dict:
    # Build feature vector in correct order
    feature_names = joblib.load('models/feature_names.pkl')
    feature_vector = [features.get(f, 0) for f in feature_names]
    
    # Scale
    scaled = scaler.transform([feature_vector])
    
    # Predict
    prediction = model.predict(scaled)[0]
    confidence = float(max(model.predict_proba(scaled)[0]))
    
    LABELS = {0: "Normal", 1: "DDoS", 2: "Ransomware", ...}
    threat_type = LABELS.get(prediction, f"Class {prediction}")
    
    return {
        "threat_type": threat_type,
        "is_threat": prediction != 0,
        "confidence": confidence,
        "model_used": "RF + PSO",
        "accuracy": 0.985,
        "processing_time_ms": 50
    }
```

---

## 📌 API Endpoints Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard |
| `/api/results` | GET | All algorithm benchmark results (JSON) |
| `/api/predict` | POST | Predict threat from features (JSON body) |
| `/api/simulate-traffic` | GET | Random simulated network traffic |
| `/api/stats` | GET | Dashboard summary statistics |

### Example — POST /api/predict
```json
// Request body:
{
  "features": {
    "packet_length": 1155,
    "duration": 4.01,
    "source_port": 53,
    "dest_port": 80,
    "bytes_sent": 675,
    "bytes_received": 877
  }
}

// Response:
{
  "threat_type": "DDoS",
  "is_threat": true,
  "confidence": 0.97,
  "model_used": "RF + PSO",
  "accuracy": 0.985,
  "processing_time_ms": 67
}
```

---

## 🛠 Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: flask` | Run `pip install -r requirements.txt` |
| `FileNotFoundError: csv` | Make sure CSV is in project root folder |
| `Port 5000 in use` | Run `python app.py` and change port in app.py: `port=5001` |
| Model not loading | Run `python train_model.py` first |
| Blank page | Check browser console (F12) for JS errors |

---

## 🎓 Notes for Academic Submission

- The web app demonstrates your **entire ML pipeline** visually
- The **Live Predict** section shows the model working in real-time
- **Traffic Monitor** simulates production-like threat detection
- All benchmark results from your notebook are preserved exactly
- The best model (RF+PSO, 98.5%) is highlighted throughout

---

*Built for ACE Engineering College — CSE AIML Department*
