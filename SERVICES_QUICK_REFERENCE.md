# Production Services Quick Reference

## 🚀 Getting Started

```bash
# 1. Run setup script
cd base10-backend
./setup_services.sh

# 2. Start Redis (if not running)
docker run -d -p 6379:6379 redis:7-alpine

# 3. Start server
python app/main.py
# Or with hot reload:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📋 Service Overview

| Service | File | Purpose | Dependencies |
|---------|------|---------|--------------|
| **Notification Orchestrator** | `comms_service.py` | Smart routing: Push → SMS → Email | Twilio, Firebase, SendGrid |
| **Scheduler** | `scheduler.py` | Automated engagement (streaks, leaderboards) | APScheduler, Redis |
| **Storage/CDN** | `storage.py` | Image hosting with mobile optimization | boto3, Cloudinary |
| **Analytics** | `analytics.py` | Question health & content gaps | PostHog, TimescaleDB |
| **Redis Client** | `redis_client.py` | Cache leaderboards, rate limiting | redis |

## 🔧 Configuration Checklist

### Required (Critical)
- [x] `DATABASE_URL` - PostgreSQL connection
- [x] `SECRET_KEY` - JWT signing key
- [x] `REDIS_URL` - Cache and sessions
- [x] `STORAGE_BACKEND` - local/s3/minio

### Phase 2 (For production)
- [ ] `FIREBASE_CREDENTIALS_PATH` - Push notifications
- [ ] `SENDGRID_API_KEY` - Email delivery
- [ ] `POSTHOG_API_KEY` - Analytics tracking
- [ ] `S3_BUCKET_NAME` - Cloud storage
- [ ] `AWS_ACCESS_KEY_ID` - AWS credentials
- [ ] `CLOUDINARY_CLOUD_NAME` - Image optimization

### Phase 3 (Optional)
- [ ] `TWILIO_ACCOUNT_SID` - SMS delivery
- [ ] `TIMESCALE_URL` - Time-series metrics

## 🗓️ Scheduler Jobs

| Job | Schedule | Purpose | Notification Type |
|-----|----------|---------|-------------------|
| **Streak Check** | Daily 00:00 GMT | Reset broken streaks | LOW priority |
| **Review Reminders** | Daily 08:00 GMT | SRS reviews due (5+) | MEDIUM priority |
| **Weekly Leaderboard** | Sunday 23:00 GMT | Top 100 rankings | - |
| **Monthly Reports** | 1st of month 00:00 | Progress PDFs | Email only |

### Manual Testing
```python
# Test individual jobs
python app/services/scheduler.py
```

## 📡 API Endpoints

### Leaderboard
```bash
# Weekly rankings (top 100)
GET /api/v1/leaderboard/weekly
Authorization: Bearer {token}

Response:
{
  "period": "weekly",
  "updated_at": "2024-12-14T...",
  "leaderboard": [
    {"rank": 1, "user_id": 123, "name": "Alice", "attempts": 450, "accuracy": 92.5}
  ],
  "user_rank": 15
}

# My current rank
GET /api/v1/leaderboard/my-rank
Authorization: Bearer {token}
```

## 🎯 Smart Notification Routing

### Decision Tree
```
User.has_app_installed?
├─ TRUE → Send Push (FREE)
└─ FALSE → Priority?
           ├─ LOW → Email only
           ├─ MEDIUM → Email
           ├─ HIGH → SMS + Email
           └─ CRITICAL → SMS + Email + Push
```

### Code Example
```python
from app.services.comms_service import (
    CommunicationService, MessageType, MessagePriority
)

comms = CommunicationService()

# Streak reminder (cheap)
comms.send_notification(
    user_id=123,
    message_type=MessageType.STREAK_REMINDER,
    priority=MessagePriority.LOW,  # Email only if no app
    content={
        'streak_days': 7,
        'message': 'Keep your 7-day streak alive! 🔥'
    }
)

# Password reset (urgent)
comms.send_notification(
    user_id=456,
    message_type=MessageType.PASSWORD_RESET,
    priority=MessagePriority.HIGH,  # SMS if no app
    content={
        'reset_code': '123456',
        'expires_in': 15
    }
)
```

## 💾 Storage Usage

### Upload Image
```python
from app.services.storage import StorageService, AssetType

storage = StorageService()

with open('biology_diagram.png', 'rb') as f:
    url = storage.upload_image(
        file=f,
        asset_type=AssetType.QUESTION_DIAGRAM,
        filename='biology_diagram.png',
        metadata={'subject': 'Biology', 'topic': 'Cell'}
    )
    
print(f"Image URL: {url}")
```

### Get Optimized URL
```python
from app.services.storage import ImageSize

# For 3G user (400px)
small_url = storage.get_image_url(
    file_path='questions/2025/12/abc123.png',
    size=ImageSize.SMALL
)

# For WiFi user (1200px)
large_url = storage.get_image_url(
    file_path='questions/2025/12/abc123.png',
    size=ImageSize.LARGE
)
```

## 📊 Analytics Tracking

### Track Question Attempt
```python
from app.services.analytics import AnalyticsService

analytics = AnalyticsService()

analytics.track_question_attempt(
    user_id=123,
    question_id=456,
    is_correct=False,
    time_spent_seconds=45,
    viewed_explanation=True,
    skipped=False
)
```

### Get Question Health Report
```python
report = analytics.get_question_health_report(
    question_id=456,
    days=30
)

print(f"Health Score: {report['health_score']}/100")
print(f"Correct Rate: {report['metrics']['correct_rate']}")
print(f"Recommendation: {report['recommendation']}")

# Example output:
# Health Score: 45.2/100
# Correct Rate: 0.35
# Recommendation: URGENT: Review question clarity
```

### Track Content Gap
```python
analytics.track_search(
    user_id=123,
    query='cryptocurrency basics',
    results_count=0,  # Content gap!
    subjects_searched=['Economics']
)

# Check logs for:
# 🔍 Content gap: User searched 'cryptocurrency basics' but no results found
```

## 🗂️ Redis Cache Operations

### Leaderboard Cache
```python
from app.core.redis_client import redis_client

# Store leaderboard
leaderboard = [
    {'rank': 1, 'user_id': 123, 'name': 'Alice', 'score': 950},
    {'rank': 2, 'user_id': 456, 'name': 'Bob', 'score': 920}
]
redis_client.set_leaderboard(leaderboard, period='weekly', ttl=3600)

# Retrieve leaderboard
cached = redis_client.get_leaderboard('weekly')

# Clear cache (e.g., for testing)
redis_client.clear_leaderboard_cache()
```

### Rate Limiting
```python
# Track API requests per user
rate_key = f'rate_limit:api:{user_id}'
count = redis_client.increment(rate_key)

if count == 1:
    redis_client.client.expire(rate_key, 60)  # 60-second window

if count > 100:
    raise HTTPException(status_code=429, detail='Rate limit exceeded')
```

## 🔍 Troubleshooting

### Scheduler not running
```bash
# Check if scheduler started
docker logs base10-backend | grep "Scheduler started"

# Expected output:
# ⏰ Scheduler started - automated engagement active!

# If not found:
# 1. Check imports: from app.services.scheduler import start_scheduler
# 2. Check database connection
# 3. Check APScheduler installed: pip show apscheduler
```

### Redis connection failed
```bash
# Test Redis
redis-cli ping
# Should return: PONG

# If failed, start Redis:
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Or check if port is occupied:
lsof -i :6379
```

### Leaderboard returns 503
```bash
# Cache not populated yet (scheduler runs Sunday 23:00)
# Manually trigger:
python -c "from app.services.scheduler import calculate_weekly_leaderboard; calculate_weekly_leaderboard()"

# Check cache:
redis-cli
> GET leaderboard:weekly
```

### Images not uploading (S3)
```bash
# Test AWS credentials
aws s3 ls s3://base10-media

# Check .env config:
grep STORAGE_BACKEND .env  # Should be: s3
grep S3_BUCKET_NAME .env
grep AWS_ACCESS_KEY_ID .env

# Test with local storage first:
echo "STORAGE_BACKEND=local" >> .env
```

## 📈 Monitoring Commands

### Check Redis Status
```bash
redis-cli INFO stats
redis-cli DBSIZE
redis-cli --latency-history
```

### Check Database
```bash
psql $DATABASE_URL -c "SELECT COUNT(*) FROM users WHERE has_app_installed = true;"
psql $DATABASE_URL -c "SELECT AVG(study_streak) FROM users WHERE study_streak > 0;"
```

### Check Scheduler Logs
```bash
# In production
docker logs base10-backend -f | grep "📊\\|✅\\|❌"

# Locally
tail -f logs/scheduler.log
```

## 💰 Cost Tracking

### Estimate Monthly Costs
```python
# Calculate SMS usage
from app.db.session import SessionLocal
from app.models.user import User

db = SessionLocal()
total_users = db.query(User).count()
users_without_app = db.query(User).filter(User.has_app_installed == False).count()

# Assuming 1 notification/day
sms_per_month = users_without_app * 30
cost_per_sms = 0.04  # Twilio average

monthly_sms_cost = sms_per_month * cost_per_sms

print(f"Users: {total_users}")
print(f"Without app: {users_without_app} ({users_without_app/total_users*100:.1f}%)")
print(f"SMS/month: {sms_per_month}")
print(f"Cost: ${monthly_sms_cost:.2f}")
```

## 🎓 Learning Resources

### Services Architecture
- [APScheduler Docs](https://apscheduler.readthedocs.io/)
- [Redis Python Client](https://redis-py.readthedocs.io/)
- [Twilio SMS API](https://www.twilio.com/docs/sms)
- [PostHog Analytics](https://posthog.com/docs)
- [AWS S3 Python SDK](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [Cloudinary API](https://cloudinary.com/documentation)

### Production Deployment
- [Docker Compose for Microservices](https://docs.docker.com/compose/)
- [Redis Persistence](https://redis.io/docs/management/persistence/)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [Monitoring with Prometheus](https://prometheus.io/docs/introduction/overview/)

---

**Need help?** Check `PRODUCTION_SERVICES_INTEGRATION.md` for detailed setup guide.
