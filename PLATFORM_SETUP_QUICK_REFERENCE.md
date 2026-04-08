# Quick Platform Setup Reference

## 🎯 Choose Your Platform

---

### **Railway.app** ⭐ (RECOMMENDED - Easiest)

1. Push to GitHub
2. Connect GitHub at railway.app
3. Create new project → select your repo
4. Go to **Variables** tab → Add:

```
FLASK_ENV=production
SECRET_KEY=<paste key below>
DEBUG=False
```

**Generate your SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Deploy automatically! 🚀

---

### **Render.com** ✅ (Free, Easy)

1. Push to GitHub
2. Go to render.com → New → Web Service
3. Connect GitHub repo
4. Settings:
   - **Runtime:** Python 3
   - **Build:** `pip install -r requirements.txt`
   - **Start:** `gunicorn app:app --bind 0.0.0.0:$PORT`

5. Go to **Environment** → Add:
```
FLASK_ENV=production
SECRET_KEY=<your-key>
DEBUG=False
```

Deploy! ✅

---

### **Heroku** 🔵 (Classic)

1. Install Heroku CLI
2. ```bash
   heroku login
   heroku create your-app-name
   
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=<your-key>
   heroku config:set DEBUG=False
   
   git push heroku main
   heroku open
   ```

Already have `Procfile` ✓

---

### **PythonAnywhere** 🐍 (Beginner-Friendly)

1. Sign up at pythonanywhere.com
2. Upload all project files
3. Bash console:
   ```bash
   pip install -r requirements.txt
   python train_model.py
   ```
4. **Web tab** → Create Flask app
5. Point to `app.py`
6. In WSGI file, add at top:
   ```python
   import os
   os.environ['FLASK_ENV'] = 'production'
   os.environ['SECRET_KEY'] = 'your-secret-key'
   os.environ['DEBUG'] = 'False'
   ```
7. Reload

---

### **AWS (EC2)** ☁️

1. Launch EC2 instance (Ubuntu)
2. SSH into server:
   ```bash
   git clone <your-repo>
   cd cyber-threat-detector
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python train_model.py
   ```

3. Create `.env`:
   ```bash
   cat > .env << 'EOF'
   FLASK_ENV=production
   SECRET_KEY=your-secret-key
   DEBUG=False
   HOST=0.0.0.0
   PORT=80
   WORKERS=4
   EOF
   ```

4. Run with Gunicorn:
   ```bash
   gunicorn app:app --bind 0.0.0.0:80 --workers 4 --daemon
   ```

5. Access at `http://your-server-ip`

---

### **Google Cloud Run** ☁️

1. ```bash
   gcloud run deploy cyber-threat-detector \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars FLASK_ENV=production,SECRET_KEY=your-key,DEBUG=False
   ```

---

### **DigitalOcean App Platform** 💧

1. Create `app.yaml`:
   ```yaml
   name: cyber-threat-detector
   services:
     - name: web
       github:
         repo: username/cyber-threat-detector
         branch: main
       build_command: pip install -r requirements.txt
       run_command: gunicorn app:app --bind 0.0.0.0:$PORT
       http_port: 5000
       envs:
         - key: FLASK_ENV
           value: production
         - key: SECRET_KEY
           scope: RUN_AND_BUILD_TIME
           value: ${SECRET_KEY}
   ```

2. Deploy from DigitalOcean console

---

## 🔐 Generate SECRET_KEY (Copy & Paste)

Run this in terminal:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Output example:
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z
```

Copy this value to your `SECRET_KEY` environment variable.

---

## ✅ Essential Env Vars (All Platforms)

| Variable | Value | Why? |
|----------|-------|------|
| `FLASK_ENV` | `production` | Disables debug mode |
| `SECRET_KEY` | `<random-32+>` | Secures session cookies |
| `DEBUG` | `False` | Hides errors from users |

🚨 **NEVER commit these to Git!** Use platform's secret manager.

---

## 🧪 Test Locally Before Deploying

```bash
# Copy example to .env
cp .env.example .env

# Edit .env and add your SECRET_KEY

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# Run app
python app.py
```

Visit: http://localhost:5000

---

## 💡 Quick Comparison

| Platform | Setup Time | Cost | Scale | Recommendation |
|----------|:----------:|:----:|:-----:|---|
| Railway | 5 min | Free tier | Excellent | ⭐ Best for beginners |
| Render | 10 min | Free tier | Good | ✅ Good alternative |
| Heroku | 10 min | $7+/month | Good | Classic choice |
| PythonAnywhere | 15 min | Free tier | Medium | Good for learning |
| AWS | 20 min | Pay-as-you-go | Excellent | Enterprise |
| Google Cloud | 15 min | Free credits | Excellent | Modern approach |
| DigitalOcean | 10 min | $5+/month | Good | Predictable cost |

---

## 📞 Environment Variable Help

**Q: Where do I find the environment variables section?**

- **Railway:** Project → Settings → Variables
- **Render:** Web Service → Environment → Environment Variables  
- **Heroku:** App → Settings → Config Vars
- **AWS:** Nginx config or Systemd service file
- **Google Cloud:** Deployment settings or Cloud Run UI

**Q: What's a SECRET_KEY?**

An encryption key Flask uses to sign session cookies. It must be:
- Random
- Long (32+ characters)
- Unique per environment
- Never changed (or users get logged out)

**Q: Can I use the same SECRET_KEY everywhere?**

❌ NO! Security risk.  
✅ Generate unique ones for each environment:
- Local dev
- Staging
- Production

**Q: Can I put my `.env` in Git?**

❌ NO! It contains secrets.  
✅ Add `.env` to `.gitignore` (already done ✓)  
✅ Share `.env.example` with other developers

---

Generated: 2026-04-08 | Version: 1.0
