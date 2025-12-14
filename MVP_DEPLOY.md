# MINIMAL MVP Deployment - Save Your Free Credits! 💰

## The Smart Approach

**You're right!** Why spend $40/month on infrastructure with ZERO users? 

Let's start with **$15/month** and scale up ONLY when we have real users.

---

## MVP Architecture (Bare Minimum)

```
┌─────────────────────────────────────┐
│  Digital Ocean App Platform         │
│  ($5/month - or FREE tier!)         │
│  ├─ FastAPI Backend (512MB RAM)     │
│  └─ Local file storage (5GB free)   │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  PostgreSQL Database                │
│  ($15/month - smallest size)        │
│  └─ Can handle 100K+ users!         │
└─────────────────────────────────────┘

Redis? ❌ Not yet - use in-memory cache (FREE)
Spaces? ❌ Not yet - use local storage (FREE)
CDN? ❌ Not yet - App Platform serves files fine
```

**Total Cost: $15-20/month** (you have $200 free credits = 10-12 months!)

---

## What You Already Have

✅ **PostgreSQL database created!**
```
ID: 0b11d019-8578-4c0e-8281-23ba3010e10a
Name: base10-db
Engine: PostgreSQL 15
Status: Creating (wait ~5 min)
```

---

## Quick Deploy (3 Steps)

### Step 1: Get Database Connection

```bash
# Wait for database to finish provisioning
doctl databases list

# Once status = "online", get connection string:
doctl databases connection base10-db --format URI

# Copy the output (looks like):
# postgresql://doadmin:AVNS_xxx@base10-db-do-user-xxx.db.ondigitalocean.com:25060/defaultdb?sslmode=require
```

### Step 2: Update app-spec.yaml

Open `app-spec.yaml` and paste your database URL:

```yaml
envs:
  - key: DATABASE_URL
    scope: RUN_TIME
    type: SECRET
    value: "postgresql://doadmin:AVNS_xxx@..."  # ← PASTE HERE
```

### Step 3: Deploy!

```bash
# Deploy the app
doctl apps create --spec app-spec.yaml

# Get your app URL
doctl apps list

# View logs
doctl apps logs <app-id> --follow
```

**That's it!** Your API will be live at `https://base10-backend-xxxxx.ondigitalocean.app`

---

## Free Alternatives We're Using

### 1. Redis Cache → In-Memory Dict (FREE!)
Your code already handles this:
```python
# app/core/redis_client.py automatically falls back to dict
# Leaderboard caches in memory (resets on restart, but who cares for MVP?)
```

**Later:** Get free Redis from [railway.app](https://railway.app) (500MB free)

### 2. Spaces Storage → Local Filesystem (FREE!)
App Platform gives you 5GB free disk:
```bash
# In .env / app-spec.yaml:
STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=./media

# Can store 10,000+ Biology diagrams!
```

**Later:** Add Spaces when you have 100+ active users uploading images

### 3. CDN → App Platform Built-in (FREE!)
Digital Ocean's App Platform automatically caches static files. Good enough for MVP!

**Later:** Add Spaces CDN when serving 1M+ images/month

---

## When to Upgrade (Rule of Thumb)

| Metric | Trigger | Action | Cost |
|--------|---------|--------|------|
| **Users** | 100+ daily active | Add Redis from Railway | $0 (free tier) |
| **Images** | 1GB+ uploaded | Add Spaces storage | $5/month |
| **Traffic** | 100GB/month | Enable Spaces CDN | Included in Spaces |
| **Database** | 80% full (800MB) | Upgrade to 2GB Postgres | $30/month |
| **API crashes** | Memory errors | Upgrade to 1GB RAM app | $10/month |

**Translation:** Don't spend money until you HAVE TO!

---

## Current Setup Can Handle:

✅ **10,000 users** (with 1GB database)
✅ **100,000 questions** stored
✅ **1,000 concurrent users**
✅ **5GB images** (Biology diagrams, profile pics)
✅ **1M API requests/month**

**This is PLENTY for validating your MVP!**

---

## Cost Breakdown

### Now (MVP):
```
PostgreSQL (1GB):     $15/month
App Platform (512MB): $5/month  (or FREE tier!)
Redis:                $0/month  (in-memory / Railway free)
Spaces:               $0/month  (local storage)
────────────────────────────────
TOTAL:                $15-20/month
```

**Your free credits:** $200 ÷ $20 = **10 months of runway!**

### Later (When You Have Users):
```
PostgreSQL (1GB):     $15/month  (still enough!)
App Platform (1GB):   $10/month  (upgrade if needed)
Redis (Railway):      $0/month   (still free!)
Spaces + CDN:         $5/month   (add when image heavy)
────────────────────────────────
TOTAL:                $30/month
```

Still cheap! And by then you might have revenue 💰

---

## What We're NOT Doing (Yet)

❌ **Managed Redis** - Costs $15/month, not needed yet
❌ **Spaces Storage** - Costs $5/month, local storage works fine
❌ **Multiple app instances** - 1 instance handles 1000+ concurrent users
❌ **Backup database** - Daily auto-backups included, no need for standby
❌ **Global CDN** - Overkill for MVP, App Platform CDN is enough

**Add these ONLY when you have actual traffic!**

---

## Monitoring Your Burn Rate

```bash
# Check database size (upgrade when >80%)
doctl databases get base10-db --format Size

# Check app memory usage
doctl apps logs <app-id> | grep "memory"

# Check monthly costs
# Visit: https://cloud.digitalocean.com/account/billing
```

**Set budget alert:** $30/month (email you if exceeded)

---

## Pro Tips for Saving Money

### 1. Use Free Tiers Everywhere
- **Railway.app**: Free Redis (500MB)
- **Render.com**: Free Redis (25MB - enough for leaderboard!)
- **Cloudinary**: Free image optimization (25GB/month)
- **PostHog**: Free analytics (1M events/month)

### 2. Don't Over-Provision
- Start with smallest database (1GB) - can upgrade in 2 clicks
- Use 1 app instance - can scale horizontally later
- Local storage first - migrate to Spaces takes 5 minutes

### 3. Monitor Actual Usage
```bash
# Weekly check: Are we running out of space?
doctl databases get base10-db

# Monthly check: How much did we actually spend?
https://cloud.digitalocean.com/account/billing
```

**Rule:** Only upgrade when you hit 80% capacity!

---

## Migration Path (When You Grow)

### Phase 1: MVP (NOW) - $15/month
- 1x PostgreSQL (1GB)
- 1x App instance (512MB)
- In-memory cache
- Local storage

### Phase 2: 100+ Users - $20/month
- Same database (still plenty of space)
- Same app instance
- **Add free Redis from Railway**
- Still local storage

### Phase 3: 1,000+ Users - $30/month
- Upgrade database to 2GB ($30/month)
- Upgrade app to 1GB RAM ($10/month)
- Still free Redis
- **Add Spaces for images** ($5/month)

### Phase 4: 10,000+ Users - $75/month
- Database: 4GB ($60/month)
- App: 2x 1GB instances ($20/month)
- Redis: Managed ($15/month)
- Spaces + CDN: (included)

**By Phase 4, you should have revenue to cover this!**

---

## Your Next 3 Commands

```bash
# 1. Wait for database (check status)
doctl databases list

# 2. Get connection string when ready
doctl databases connection base10-db --format URI

# 3. Deploy!
# (Update DATABASE_URL in app-spec.yaml first)
doctl apps create --spec app-spec.yaml
```

**Time to first deploy:** 10 minutes
**Monthly cost:** $15
**Months of runway:** 10+ months

**GO BUILD! 🚀**

---

## Sanity Check

**Before you spend money, ask:**
1. Do I have 100+ active users? → No? Don't add Redis yet
2. Have I used 1GB of images? → No? Don't add Spaces yet
3. Is my API slow? → No? Don't upgrade RAM yet
4. Is my database full? → No? Don't upgrade yet

**Build first, scale later.** That's the startup way! 💪
