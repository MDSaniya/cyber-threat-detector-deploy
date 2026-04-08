# Environment Variables Guide - Platform-Specific

## 🚀 Quick Reference

Choose your deployment platform and follow the instructions:

---

## 1️⃣ Railway.app (Recommended)

### Environment Variables to Set

```
FLASK_ENV=production
FLASK_APP=app.py
SECRET_KEY=<generate-random-key>
DEBUG=False
PORT=5000
HOST=0.0.0.0
LOG_LEVEL=INFO
```

### How to Add on Railway

1. Go to your Railway project
2. Click **Settings** (gear icon)
3. Go to **Variables** tab
4. Add each key-value pair:
   - Key: `SECRET_KEY`, Value: `<your-secret-key>`
   - Key: `FLASK_ENV`, Value: `production`
   - Key: `DEBUG`, Value: `False`
   - etc.

### Generate SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 2️⃣ Render.com

### Essential Environment Variables

```
FLASK_ENV=production
FLASK_APP=app.py
SECRET_KEY=<generate-random-key>
DEBUG=False
HOST=0.0.0.0
PORT=5000
WORKERS=2
```

### How to Add on Render

1. Go to your Web Service
2. Click **Environment**
3. Add variables in **Environment Variables** section:
   ```
   FLASK_ENV=production
   SECRET_KEY=<your-key>
   DEBUG=False
   ```

### Start Command Required

```bash
gunicorn app:app --bind 0.0.0.0:$PORT --workers 2
```

---

## 3️⃣ Heroku

### Required Environment Variables

```
FLASK_ENV=production
FLASK_APP=app.py
SECRET_KEY=<generate-random-key>
DEBUG=False
```

### How to Add on Heroku

**Via Heroku CLI:**
```bash
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=<your-secret-key>
heroku config:set DEBUG=False
```

**Via Heroku Dashboard:**
1. Go to your app → **Settings**
2. Click **Reveal Config Vars**
3. Add key-value pairs

### Required Files

- `Procfile` (already created ✓)
- `requirements.txt` (already created ✓)
- `runtime.txt` (already created - specifies Python 3.11 ✓)

---

## 4️⃣ PythonAnywhere

### Environment Variables to Add

```
FLASK_ENV=production
FLASK_APP=app.py
SECRET_KEY=<generate-random-key>
DEBUG=False
```

### How to Add on PythonAnywhere

1. Go to **Web tab**
2. Find your web app → **Reload**
3. In WSGI file, set at the top:

```python
import os
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'your-secret-key'
os.environ['DEBUG'] = 'False'
```

---

## 5️⃣ AWS (EC2 / Lightsail)

### Create `.env` file on server

```bash
cat > .env << EOF
FLASK_ENV=production
FLASK_APP=app.py
SECRET_KEY=your-secret-key
DEBUG=False
HOST=0.0.0.0
PORT=80
WORKERS=4
EOF
```

### Or use Systemd Service

Create `/etc/systemd/system/cyberfeddefender.service`:

```ini
[Unit]
Description=CyberFedDefender Flask App
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/cyber-threat-detector
Environment="FLASK_ENV=production"
Environment="SECRET_KEY=your-secret-key"
Environment="DEBUG=False"
ExecStart=/var/www/cyber-threat-detector/venv/bin/gunicorn app:app --bind 0.0.0.0:80

[Install]
WantedBy=multi-user.target
```

### Or use `.env` with python-dotenv

```bash
pip install python-dotenv
```

Update `app.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

---

## 6️⃣ Google Cloud (Cloud Run)

### Build & Deploy

```bash
gcloud run deploy cyber-threat-detector \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars FLASK_ENV=production,SECRET_KEY=your-key,DEBUG=False
```

### Or via Console

1. Go to **Cloud Run**
2. Create Service
3. Deploy Container
4. Set environment variables in deployment config

---

## 7️⃣ DigitalOcean App Platform

### Environment Variables in `app.yaml`

```yaml
name: cyber-threat-detector
services:
  - name: web
    github:
      repo: your-username/cyber-threat-detector
      branch: main
    build_command: pip install -r requirements.txt
    run_command: gunicorn app:app
    envs:
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        value: ${SECRET_KEY}
      - key: DEBUG
        value: "False"
```

---

## 🔐 Critical Environment Variables Explained

### FLASK_ENV
- **Value**: `production` (NEVER `development`)
- **Purpose**: Disables hot-reload and debug tools
- **Why**: Security - prevents internal errors from leaking

### SECRET_KEY
- **Value**: Random 32+ character string (generate below)
- **Purpose**: Encrypts session cookies and CSRF tokens
- **Why**: Without it, session data can be forged
- **Generate**: `python -c "import secrets; print(secrets.token_hex(32))"`

### DEBUG
- **Value**: `False` (NEVER `True`)
- **Purpose**: Hides detailed error messages from users
- **Why**: Debug page shows file paths and code - huge security risk

### HOST
- **Value**: `0.0.0.0` (listen on all interfaces)
- **Purpose**: Allows external connections to your server
- **Why**: Default `127.0.0.1` only accepts localhost

### PORT
- **Value**: `5000` (or `80`/`443` for production)
- **Purpose**: Which network port to run on
- **Why**: Railway/Render passes `$PORT` environment variable

### WORKERS
- **Value**: `(CPU_cores × 2) + 1`
- **Example**: 4 CPU cores = 9 workers
- **Purpose**: Gunicorn concurrency - handles multiple requests
- **Why**: 1 worker = app hangs when processing one request

---

## 🔄 Full Minimal Setup (All Platforms)

### Absolute Minimum (copy & paste this):

```
FLASK_ENV=production
FLASK_APP=app.py
SECRET_KEY=<RUN THIS: python -c "import secrets; print(secrets.token_hex(32))">
DEBUG=False
```

### Recommended Production Setup:

```
FLASK_ENV=production
FLASK_APP=app.py
SECRET_KEY=<generate-above>
DEBUG=False
HOST=0.0.0.0
WORKERS=4
LOG_LEVEL=INFO
APP_NAME=CyberFedDefender
```

---

## 📋 Platform Checklist

| Platform | SECRET_KEY | FLASK_ENV | DEBUG | PORT | Start Command |
|----------|:----------:|:---------:|:-----:|:----:|----------------|
| Railway | ✓ | ✓ | ✓ | Auto | Auto |
| Render | ✓ | ✓ | ✓ | $PORT | gunicorn |
| Heroku | ✓ | ✓ | ✓ | Procfile | Procfile |
| PythonAnywhere | ✓ | ✓ | ✓ | Auto | WSGI |
| AWS | ✓ | ✓ | ✓ | Custom | gunicorn |
| Google Cloud | ✓ | ✓ | ✓ | $PORT | Custom |
| DigitalOcean | ✓ | ✓ | ✓ | Auto | YAML |

---

## 🛡️ Security Best Practices

1. **Generate unique SECRET_KEY for EACH environment**:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Never commit `.env` to Git** (already in `.gitignore` ✓)

3. **Use platform's secret vault**:
   - Railway: Settings → Variables (marked as "Secret")
   - Render: Environment → Secret File option
   - Heroku: Settings → Config Vars
   - AWS: Secrets Manager
   - GCP: Secret Manager

4. **Rotate keys regularly**:
   - Change SECRET_KEY every 3-6 months
   - Rotate API keys annually

5. **Use HTTPS only**:
   - All platforms enforce HTTPS by default ✓

---

## ⚠️ Common Mistakes

❌ Using same SECRET_KEY across dev/staging/production  
❌ Committing `.env` file to Git  
❌ Setting `DEBUG=True` in production  
❌ Using weak SECRET_KEY (too short)  
❌ Storing API keys in code instead of env vars  
❌ Not setting `HOST=0.0.0.0` (blocks external access)  
❌ Using 1 Gunicorn worker (app hangs easily)  

---

## ✅ Verification

After setting env vars, test locally:

```bash
# Windows
set FLASK_ENV=production
set DEBUG=False
python app.py

# Mac/Linux
export FLASK_ENV=production
export DEBUG=False
python app.py
```

Check Flask logs for:
```
✓ Running on http://0.0.0.0:5000
✓ WARNING in app.run(): This is a development server. Do not use it in production.
```

The warning is expected - Gunicorn will replace it in production.
