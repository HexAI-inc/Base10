# Quick Deploy to Digital Ocean (Web UI) 🚀

Your code is now on GitHub! Let's deploy via Digital Ocean's web interface (easier than CLI for GitHub auth).

## Step 1: Connect GitHub to Digital Ocean

1. Go to: https://cloud.digitalocean.com/apps/new
2. Click **"GitHub"** as source
3. Click **"Authorize Digital Ocean"** (first time only)
4. Select repository: **`HexAI-inc/Base10`**
5. Select branch: **`main`**
6. Click **"Next"**

## Step 2: Configure App

### Resources Tab:
- **Type**: Web Service
- **Name**: `base10-api`
- **Dockerfile Path**: `Dockerfile` (auto-detected!)
- **HTTP Port**: `8080`
- **HTTP Path**: `/` 

### Environment Variables:
Click **"Edit"** and add these:

```
DATABASE_URL = <your-database-url-from-DO-dashboard>

SECRET_KEY = <secret key>

REDIS_URL = redis://localhost:6379/0

STORAGE_BACKEND = local

LOCAL_STORAGE_PATH = ./media

ALGORITHM = HS256

ACCESS_TOKEN_EXPIRE_MINUTES = 10080

ENVIRONMENT = production

BACKEND_CORS_ORIGINS = ["*"]
```

*Mark DATABASE_URL and SECRET_KEY as **encrypted** ✅*

### Plan:
- **Instance Size**: Basic ($5/month)
- **Instance Count**: 1

## Step 3: Review & Deploy

- **App Name**: `base10-backend`
- **Region**: New York (NYC3)
- **Total Cost**: $5/month (app) + $15/month (database) = **$20/month**

Click **"Create Resources"**

## Step 4: Wait for Deployment (3-5 minutes)

Watch the build logs:
- Installing dependencies...
- Building Docker image...
- Deploying...

## Step 5: Get Your API URL

Once deployed, you'll see:
```
https://base10-backend-xxxxx.ondigitalocean.app
```

Test it:
```bash
curl https://base10-backend-xxxxx.ondigitalocean.app/health
# Should return: {"status": "healthy"}

# View API docs:
open https://base10-backend-xxxxx.ondigitalocean.app/docs
```

## Step 6: Run Database Migration

```bash
# Get your app URL from DO dashboard
export API_URL="https://base10-backend-xxxxx.ondigitalocean.app"

# Run migration locally pointing to DO database
export DATABASE_URL="<get-from-DO-dashboard>"

python migrate_engagement_fields.py
```

## Auto-Deploy on Git Push

Now whenever you push to GitHub:
```bash
git add .
git commit -m "Update API"
git push origin main
```

Digital Ocean **automatically rebuilds and deploys** in ~3 minutes! 🚀

---

## Troubleshooting

### Build fails?
Check logs in DO dashboard:
- https://cloud.digitalocean.com/apps/[your-app-id]/logs

### Can't connect to database?
Test connection:
```bash
# Get connection string from DO dashboard
psql "<your-database-url>"
```

### App crashes?
Check runtime logs:
```bash
doctl apps logs <app-id> --follow --type run
```

---

## Next: Add Custom Domain (Optional)

1. Go to app settings → Domains
2. Add: `api.base10.education`
3. Configure DNS:
   ```
   CNAME api → base10-backend-xxxxx.ondigitalocean.app
   ```
4. SSL auto-configured by DO!

---

**Your API will be live in 5 minutes!** 🎉

Start here: https://cloud.digitalocean.com/apps/new
