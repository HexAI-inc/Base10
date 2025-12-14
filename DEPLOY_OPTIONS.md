# Quick Deploy to Digital Ocean App Platform

## Option 1: Deploy from GitHub (Recommended)

```bash
cd /home/c_jalloh/Documents/IndabaX/base10-backend

# Initialize git repo
git init
git add .
git commit -m "Initial commit - Base10 backend"

# Create GitHub repo (go to github.com/new)
# Then push:
git remote add origin https://github.com/YOUR-USERNAME/base10-backend.git
git branch -M main
git push -u origin main

# Update app-spec.yaml with your repo:
# github:
#   repo: YOUR-USERNAME/base10-backend
#   branch: main

# Deploy
doctl apps create --spec app-spec.yaml
```

## Option 2: Deploy using DO CLI (No GitHub needed)

Digital Ocean App Platform requires a source. Let's use their direct upload:

```bash
cd /home/c_jalloh/Documents/IndabaX/base10-backend

# Create a simple app using DO's builder
doctl apps create \
  --build-command "pip install -r requirements.txt" \
  --run-command "uvicorn app.main:app --host 0.0.0.0 --port 8080" \
  --http-port 8080 \
  --region nyc \
  base10-backend

# This won't work without source, so we need GitHub or Docker registry
```

## Option 3: Manual Docker Build + Deploy (Fastest for now)

Since DO App Platform needs a source, let's use **Railway.app** or **Render.com** instead (they're easier for MVP):

### Using Render.com (FREE tier!)

1. Go to https://render.com
2. Sign in with GitHub
3. Push your code to GitHub (see Option 1)
4. Click "New +" → "Web Service"
5. Connect your GitHub repo
6. Settings:
   - **Environment**: Docker
   - **Region**: Oregon (US West)
   - **Instance Type**: Free
7. Add environment variables:
   ```
   DATABASE_URL=<YOUR_DO_DATABASE_URL>
   SECRET_KEY=<GENERATE_WITH_OPENSSL>
   REDIS_URL=redis://localhost:6379/0
   STORAGE_BACKEND=local
   LOCAL_STORAGE_PATH=./media
   ```
8. Click "Create Web Service"

**Cost: $0/month** (Free tier includes 750 hours/month)

### Using Railway.app (Also FREE!)

1. Go to https://railway.app
2. Sign in with GitHub  
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repo
5. Railway auto-detects Dockerfile
6. Add environment variables (same as above)
7. Deploy!

**Cost: $5/month credit free** (enough for MVP)

---

## The Problem with Digital Ocean App Platform

DO App Platform requires one of:
- GitHub repo (public or private)
- GitLab repo
- Docker registry (DockerHub, GitHub Container Registry)
- Direct source upload (not supported via CLI)

**Solution**: Push to GitHub first, then deploy.

---

## Quick GitHub Push

```bash
cd /home/c_jalloh/Documents/IndabaX/base10-backend

# Initialize repo
git init
git add .
git commit -m "Base10 backend - MVP"

# Create repo on GitHub: https://github.com/new
# Name: base10-backend
# Public or Private: Private (for now)

# Push
git remote add origin https://github.com/YOUR-USERNAME/base10-backend.git
git branch -M main
git push -u origin main
```

Then update `app-spec.yaml`:

```yaml
services:
  - name: api
    github:
      repo: YOUR-USERNAME/base10-backend
      branch: main
      deploy_on_push: true
```

And deploy:

```bash
doctl apps create --spec app-spec.yaml
```

---

## Recommendation for MVP

**Use Render.com FREE tier:**
- ✅ No GitHub setup needed initially
- ✅ Free tier (750 hours/month = always on)
- ✅ Auto-deploys from GitHub
- ✅ Built-in SSL
- ✅ Health checks
- ✅ Can connect to your DO PostgreSQL

**Save DO App Platform for later** when you:
- Have paying users
- Need better performance ($5/month)
- Want multi-region deployment

---

## Next Command (Choose One)

**A) GitHub + DO App Platform:**
```bash
# Push to GitHub first, then:
doctl apps create --spec app-spec.yaml
```

**B) Render.com (Easiest):**
```bash
# Just push to GitHub, then use Render web UI
# No doctl needed!
```

**C) Railway.app (Also Easy):**
```bash
# Push to GitHub, use Railway web UI
```

Which option do you prefer?
