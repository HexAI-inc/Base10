# Digital Ocean Deployment for Base10

## Architecture Overview

### Digital Ocean Services Used:
1. **App Platform** - Deploy FastAPI backend (manages containers automatically)
2. **Managed PostgreSQL** - Database with daily backups
3. **Managed Redis** - Cache for leaderboards
4. **Spaces (S3-compatible)** - Image storage with CDN

### Cost Estimate (MINIMAL MVP):
- App Platform: $0/month (Free tier - 1 static site OR use $5/month starter)
- PostgreSQL: $15/month (1GB RAM - smallest size)
- Redis: **USE FREE REDIS ON RAILWAY/RENDER** or local in-memory cache
- Spaces: **SKIP FOR NOW** - Use local file storage initially
**Total: ~$15-20/month MAX** (leaves you plenty of free credits!)

### Why This is Enough:
- Free tier app handles 10K+ requests/day
- 1GB PostgreSQL can handle 100K+ users
- No Redis needed initially (use in-memory cache)
- No Spaces needed (store images locally until you have users)

---

## Setup Steps

### 1. Authenticate doctl

```bash
# Get your API token from: https://cloud.digitalocean.com/account/api/tokens
doctl auth init
# Paste your token when prompted
```

### 2. Create PostgreSQL Database

```bash
# Create managed PostgreSQL cluster (nyc3 region)
doctl databases create base10-db \
  --engine pg \
  --version 15 \
  --size db-s-1vcpu-1gb \
  --region nyc3

# Wait for database to be ready (takes ~5 minutes)
doctl databases list

# Get connection string
doctl databases connection base10-db --format User,Password,Host,Port,Database
```

### 3. Redis Cache - SKIP FOR NOW (Save Money!)

**Option 1: Free Redis on Railway.app**
```bash
# Go to railway.app, create free Redis (500MB free)
# Get connection URL from Railway dashboard
```

**Option 2: Use Python dict for in-memory cache (FREE)**
```python
# In app/core/redis_client.py - fallback to dict
# Already handled in the code!
```

### 4. Image Storage - SKIP FOR NOW (Save Money!)

**For MVP: Use local filesystem**
```bash
# In .env:
STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=./media

# Later when you have users, add Spaces:
doctl spaces create base10-media --region nyc3
```

**Why this works:**
- Digital Ocean App Platform has 5GB free disk space
- Enough for 10,000+ Biology diagrams
- Can migrate to Spaces later in 5 minutesreate Spaces bucket for images
doctl spaces create base10-media --region nyc3

# Enable CDN
doctl spaces set-cors base10-media --region nyc3 --cors-config cors.json

# Get Spaces credentials
doctl spaces keys list
# Or create new key:
doctl spaces keys create base10-spaces-key
```

### 5. Deploy Backend to App Platform

```bash
# Create app using spec file
doctl apps create --spec app-spec.yaml

# Get app URL
doctl apps list

# View logs
doctl apps logs <app-id> --follow
```

---

## Configuration Files

### app-spec.yaml (Digital Ocean App Spec)

```yaml
name: base10-backend
region: nyc
services:
  - name: api
    github:
      repo: your-username/base10-backend
      branch: main
      deploy_on_push: true
    
    build_command: pip install -r requirements.txt
    run_command: uvicorn app.main:app --host 0.0.0.0 --port 8080
    
    envs:
      - key: DATABASE_URL
        scope: RUN_TIME
        type: SECRET
        value: ${db.DATABASE_URL}
      
      - key: REDIS_URL
        scope: RUN_TIME
        type: SECRET
        value: ${redis.CONNECTION_URI}
      
      - key: SECRET_KEY
        scope: RUN_TIME
        type: SECRET
        value: ${SECRET_KEY}
      
      - key: STORAGE_BACKEND
        scope: RUN_TIME
        value: s3
      
      - key: S3_BUCKET_NAME
        scope: RUN_TIME
        value: base10-media
      
      - key: AWS_ACCESS_KEY_ID
        scope: RUN_TIME
        type: SECRET
        value: ${SPACES_KEY}
      
      - key: AWS_SECRET_ACCESS_KEY
        scope: RUN_TIME
        type: SECRET
        value: ${SPACES_SECRET}
      
      - key: S3_ENDPOINT_URL
        scope: RUN_TIME
        value: https://nyc3.digitaloceanspaces.com
      
      - key: S3_CDN_DOMAIN
        scope: RUN_TIME
        value: base10-media.nyc3.cdn.digitaloceanspaces.com
    
    instance_count: 1
    instance_size_slug: basic-xxs
    
    http_port: 8080
    
    health_check:
      http_path: /health
      initial_delay_seconds: 60
      period_seconds: 10
      timeout_seconds: 5
      success_threshold: 1
      failure_threshold: 3
    
    routes:
      - path: /

databases:
  - name: base10-db
    engine: PG
    version: "15"
    size: db-s-1vcpu-1gb
    num_nodes: 1
    
  - name: base10-redis
    engine: REDIS
    version: "7"
    size: db-s-1vcpu-1gb
    num_nodes: 1
```

### cors.json (Spaces CORS Configuration)

```json
{
  "CORSRules": [
    {
      "AllowedOrigins": ["*"],
      "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
      "AllowedHeaders": ["*"],
      "MaxAgeSeconds": 3600
    }
  ]
}
```

---

## Environment Variables Setup

After creating resources, update your app environment variables:

```bash
# Set database URL
doctl apps update <app-id> --spec updated-app-spec.yaml

# Or set individual env vars
doctl apps config set <app-id> \
  --env DATABASE_URL=postgresql://user:pass@host:port/db \
  --env REDIS_URL=redis://default:pass@host:port
```

---

## Database Migration

```bash
# SSH into app container
doctl apps logs <app-id> --type run

# Or run migration locally pointing to DO database
export DATABASE_URL="postgresql://..."
python migrate_engagement_fields.py
```

---

## Deployment Commands

```bash
# Deploy new version (auto-deploys on git push)
git push origin main

# Manual deploy
doctl apps create-deployment <app-id>

# View deployment status
doctl apps get-deployment <app-id> <deployment-id>

# Rollback to previous deployment
doctl apps list-deployments <app-id>
doctl apps create-deployment <app-id> --force

# Scale up/down
doctl apps update <app-id> --spec app-spec.yaml
# (Change instance_count in yaml)
```

---

## Monitoring

```bash
# View real-time logs
doctl apps logs <app-id> --follow --type run

# View build logs
doctl apps logs <app-id> --type build

# Check app health
doctl apps get <app-id>

# Database metrics
doctl databases metrics <db-id>
```

---

## Custom Domain Setup

```bash
# Add custom domain
doctl apps update <app-id> --spec app-spec-domain.yaml

# In app-spec-domain.yaml, add:
# domains:
#   - domain: api.base10.education
#     type: PRIMARY
#     zone: base10.education

# Get DNS records to configure
doctl apps list-domains <app-id>
```

---

## Backup & Recovery

### Database Backups (Automatic)
```bash
# List backups (automatic daily backups)
doctl databases backups list base10-db

# Restore from backup
doctl databases restore base10-db <backup-id>

# Create manual backup
doctl databases backup base10-db
```

### Manual Database Backup
```bash
# Dump database
doctl databases connection base10-db
pg_dump -h <host> -U <user> -d <database> > backup.sql

# Restore
psql -h <host> -U <user> -d <database> < backup.sql
```

---

## Cost Optimization Tips

1. **Use Basic tier** ($5/month) - sufficient for MVP
2. **Enable auto-scaling** - scale down during low traffic
3. **Use Spaces CDN** - reduces bandwidth costs
4. **Monitor database size** - upgrade only when needed
5. **Use Redis for caching** - reduces database queries

---

## Troubleshooting

### App won't start
```bash
# Check build logs
doctl apps logs <app-id> --type build

# Common issues:
# - Missing requirements in requirements.txt
# - Wrong Python version
# - Port not set to 8080
```

### Database connection failed
```bash
# Verify database is ready
doctl databases get base10-db

# Check connection string
doctl databases connection base10-db

# Test connection locally
psql "postgresql://user:pass@host:port/db"
```

### Images not uploading to Spaces
```bash
# Check Spaces credentials
doctl spaces keys list

# Test Spaces access
aws s3 ls s3://base10-media \
  --endpoint-url https://nyc3.digitaloceanspaces.com \
  --access-key-id <key> \
  --secret-access-key <secret>
```

---

## Quick Deploy Script

```bash
#!/bin/bash
# deploy-to-do.sh

set -e

echo "🚀 Deploying Base10 to Digital Ocean..."

# 1. Create databases if not exist
echo "📊 Setting up databases..."
doctl databases create base10-db --engine pg --version 15 --size db-s-1vcpu-1gb --region nyc3 || true
doctl databases create base10-redis --engine redis --version 7 --size db-s-1vcpu-1gb --region nyc3 || true

# 2. Create Spaces bucket
echo "🗄️  Setting up Spaces..."
doctl spaces create base10-media --region nyc3 || true

# 3. Deploy app
echo "🚢 Deploying app..."
doctl apps create --spec app-spec.yaml

echo "✅ Deployment complete!"
echo "🔗 Get your app URL: doctl apps list"
echo "📊 View logs: doctl apps logs <app-id> --follow"
```

---

## Next Steps

1. **Authenticate doctl**: `doctl auth init`
2. **Create resources**: Run commands above or use quick deploy script
3. **Push code to GitHub**: Digital Ocean auto-deploys on push
4. **Set environment variables**: Update app spec with secrets
5. **Run database migration**: `python migrate_engagement_fields.py`
6. **Test API**: Visit `https://your-app.ondigitalocean.app/docs`
7. **Configure custom domain**: (optional) `api.base10.education`

---

## Useful Links

- [Digital Ocean Dashboard](https://cloud.digitalocean.com/)
- [App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [doctl Reference](https://docs.digitalocean.com/reference/doctl/)
- [Managed Databases](https://docs.digitalocean.com/products/databases/)
- [Spaces (S3) Docs](https://docs.digitalocean.com/products/spaces/)
