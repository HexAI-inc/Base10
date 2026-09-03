# Admin Dashboard - Quick Start Guide

## 🎯 What is This?
The admin dashboard gives you and your team complete visibility into Base10's health, user activity, content quality, and system performance. Use it to monitor the app, identify issues, and make data-driven decisions.

## 🔐 Getting Access

### Step 1: Get Admin Credentials
Admin access is restricted to team emails in the code:
```python
ADMIN_EMAILS = [
    "cjalloh25@gmail.com",
    "esjallow03@gmail.com"
]
```

### Step 2: Get Your JWT Token
```bash
# Login to get JWT token
curl -X POST "https://your-api.com/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "cjalloh25@gmail.com",
    "password": "your_password"
  }'

# Response includes: { "access_token": "eyJ..." }
```

### Step 3: Access Admin Endpoints
```bash
# Use token in Authorization header
curl -X GET "https://your-api.com/api/v1/admin/health" \
  -H "Authorization: Bearer eyJ..."
```

---

## 📊 Daily Monitoring Workflow

### Morning Check (5 minutes)
```bash
# 1. Check system health
curl "https://your-api.com/api/v1/admin/health" \
  -H "Authorization: Bearer $TOKEN"

# Look for:
# ✅ status: "healthy"
# ✅ database_connected: true
# ✅ active_users_24h > 50
# ✅ error_rate < 1%
```

### Quick Stats Dashboard
```bash
# 2. Get comprehensive summary
curl "https://your-api.com/api/v1/admin/stats/summary?time_range=today" \
  -H "Authorization: Bearer $TOKEN"

# Key metrics:
# - New users today
# - Total attempts today
# - Average accuracy
# - Pending reports
```

### Review User Reports
```bash
# 3. Check for flagged content
curl "https://your-api.com/api/v1/admin/content/quality" \
  -H "Authorization: Bearer $TOKEN"

# If pending_reports > 0, review them:
curl "https://your-api.com/api/v1/admin/questions/problematic" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔥 Common Admin Tasks

### 1. Find a User (Support)
```bash
# Search by email, phone, or name
curl "https://your-api.com/api/v1/admin/users/search?query=john" \
  -H "Authorization: Bearer $TOKEN"

# Get user details (id, email, activity, streak, points)
```

### 2. Deactivate Spam Account
```bash
# Deactivate user
curl -X PUT "https://your-api.com/api/v1/admin/users/123/deactivate?reason=spam" \
  -H "Authorization: Bearer $TOKEN"

# This sets is_active = False, user can't login
```

### 3. Delete Bad Question
```bash
# First, identify problematic questions
curl "https://your-api.com/api/v1/admin/questions/problematic?max_accuracy=0.3" \
  -H "Authorization: Bearer $TOKEN"

# Delete question if it's incorrect or inappropriate
curl -X DELETE "https://your-api.com/api/v1/admin/questions/456?reason=incorrect_answer" \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Resolve User Report
```bash
# Mark report as fixed
curl -X PUT "https://your-api.com/api/v1/admin/reports/789/resolve?action=question_fixed&notes=Fixed%20typo" \
  -H "Authorization: Bearer $TOKEN"

# Actions: dismissed, question_fixed, question_deleted
```

---

## 📈 Weekly Analytics Review

### Monday Morning Report
```bash
# 1. User growth trends
curl "https://your-api.com/api/v1/admin/users/growth" \
  -H "Authorization: Bearer $TOKEN"

# Key metrics:
# - New users this week
# - 7-day retention rate (target: >60%)
# - Churn rate (target: <20%)
# - DAU and MAU
```

### Engagement Analysis
```bash
# 2. How active are users?
curl "https://your-api.com/api/v1/admin/engagement" \
  -H "Authorization: Bearer $TOKEN"

# Check:
# - Average attempts per user
# - Study time per session
# - Completion rate (target: >70%)
# - Users with active streaks
```

### Content Quality Check
```bash
# 3. Identify content issues
curl "https://your-api.com/api/v1/admin/questions/problematic?min_attempts=100&max_accuracy=0.35" \
  -H "Authorization: Bearer $TOKEN"

# Review questions with:
# - <35% accuracy (too hard or wrong)
# - Multiple user reports
# - Fix or remove them
```

### Top Users for Marketing
```bash
# 4. Find success stories
curl "https://your-api.com/api/v1/admin/users/top?limit=10" \
  -H "Authorization: Bearer $TOKEN"

# Use for:
# - Testimonials on website
# - Case studies
# - Reward programs
# - Understanding success patterns
```

---

## 🚨 Alerts & Thresholds

### Critical (Immediate Action)
- ❌ System status: "critical"
- ❌ Database not connected
- ❌ Active users <10 in 24h
- ❌ Error rate >5%

### Warning (Review Today)
- ⚠️ System status: "degraded"
- ⚠️ Churn rate >25%
- ⚠️ 7-day retention <50%
- ⚠️ Pending reports >20
- ⚠️ Flagged questions >10

### Good Performance
- ✅ System status: "healthy"
- ✅ Active users growing
- ✅ 7-day retention >60%
- ✅ Churn rate <20%
- ✅ Average accuracy 65-75%
- ✅ Low pending reports

---

## 🛠️ Python Script for Daily Checks

Save this as `check_admin.py`:

```python
#!/usr/bin/env python3
"""
Daily admin dashboard check script.
Run: python check_admin.py
"""
import requests
import os
from datetime import datetime

BASE_URL = os.getenv("API_URL", "https://your-api.com/api/v1")
TOKEN = os.getenv("ADMIN_TOKEN", "your_token_here")

headers = {"Authorization": f"Bearer {TOKEN}"}

def check_health():
    """Check system health."""
    response = requests.get(f"{BASE_URL}/admin/health", headers=headers)
    health = response.json()
    
    print(f"\n🏥 System Health: {health['status'].upper()}")
    print(f"   Database: {'✅' if health['database_connected'] else '❌'}")
    print(f"   Active users (24h): {health['active_users_24h']}")
    print(f"   Total attempts: {health['total_attempts']:,}")
    print(f"   Average accuracy: {health['average_accuracy']}%")
    
    if health['status'] != 'healthy':
        print("   ⚠️ WARNING: System not healthy!")
    
    return health['status'] == 'healthy'

def check_growth():
    """Check user growth."""
    response = requests.get(f"{BASE_URL}/admin/users/growth", headers=headers)
    growth = response.json()
    
    print(f"\n📈 User Growth:")
    print(f"   New today: {growth['new_users_today']}")
    print(f"   New this week: {growth['new_users_this_week']}")
    print(f"   7-day retention: {growth['retention_rate_7d']}%")
    print(f"   Churn rate: {growth['churn_rate']}%")
    
    if growth['churn_rate'] > 25:
        print("   ⚠️ WARNING: High churn rate!")
    
    return growth['churn_rate'] < 25

def check_content():
    """Check content quality."""
    response = requests.get(f"{BASE_URL}/admin/content/quality", headers=headers)
    content = response.json()
    
    print(f"\n📚 Content Quality:")
    print(f"   Total questions: {content['total_questions']}")
    print(f"   Flagged: {content['flagged_questions']}")
    print(f"   Low quality: {content['low_quality_questions']}")
    print(f"   Pending reports: {content['pending_reports']}")
    
    if content['pending_reports'] > 20:
        print("   ⚠️ WARNING: Many pending reports!")
    
    return content['pending_reports'] < 20

def main():
    """Run all checks."""
    print(f"🔍 Base10 Admin Check - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    all_good = True
    all_good &= check_health()
    all_good &= check_growth()
    all_good &= check_content()
    
    print("\n" + "=" * 60)
    if all_good:
        print("✅ ALL SYSTEMS OPERATIONAL")
    else:
        print("⚠️ ISSUES DETECTED - REVIEW ABOVE")
    print()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)
```

Run it:
```bash
# Set environment variables
export API_URL="https://your-api.com/api/v1"
export ADMIN_TOKEN="your_jwt_token"

# Run daily check
python check_admin.py
```

Set up cron for automatic checks:
```bash
# Edit crontab
crontab -e

# Add line for daily 9am check
0 9 * * * cd /path/to/scripts && python check_admin.py | mail -s "Base10 Daily Report" admin@base10.app
```

---

## 📱 Mobile Monitoring (Optional)

### Use Postman or Insomnia
1. Import admin endpoints
2. Save JWT token as environment variable
3. Create collection for quick checks
4. Set up monitors for alerts

### Build Simple Web Dashboard
```html
<!DOCTYPE html>
<html>
<head>
    <title>Base10 Admin</title>
    <style>
        body { font-family: sans-serif; padding: 20px; }
        .metric { padding: 15px; margin: 10px; border-radius: 8px; }
        .healthy { background: #d4edda; }
        .warning { background: #fff3cd; }
        .critical { background: #f8d7da; }
    </style>
</head>
<body>
    <h1>Base10 Admin Dashboard</h1>
    <div id="dashboard"></div>
    
    <script>
        const API_URL = "https://your-api.com/api/v1";
        const TOKEN = localStorage.getItem("admin_token");
        
        async function loadDashboard() {
            const health = await fetch(`${API_URL}/admin/health`, {
                headers: { "Authorization": `Bearer ${TOKEN}` }
            }).then(r => r.json());
            
            const growth = await fetch(`${API_URL}/admin/users/growth`, {
                headers: { "Authorization": `Bearer ${TOKEN}` }
            }).then(r => r.json());
            
            document.getElementById("dashboard").innerHTML = `
                <div class="metric ${health.status === 'healthy' ? 'healthy' : 'critical'}">
                    <h2>System Health: ${health.status}</h2>
                    <p>Active users (24h): ${health.active_users_24h}</p>
                    <p>Average accuracy: ${health.average_accuracy}%</p>
                </div>
                <div class="metric healthy">
                    <h2>User Growth</h2>
                    <p>New today: ${growth.new_users_today}</p>
                    <p>7-day retention: ${growth.retention_rate_7d}%</p>
                </div>
            `;
        }
        
        loadDashboard();
        setInterval(loadDashboard, 60000); // Refresh every minute
    </script>
</body>
</html>
```

---

## 🎯 Success Metrics to Track

### Daily
- ✅ System uptime
- ✅ Active users (DAU)
- ✅ New registrations
- ✅ Error rate

### Weekly
- ✅ User retention (7d)
- ✅ Engagement rate
- ✅ Content quality
- ✅ Top performers

### Monthly
- ✅ User growth (MoM)
- ✅ Churn rate
- ✅ Content expansion
- ✅ Feature adoption

---

## 🔜 Roadmap

### Coming Soon
- [ ] Real-time WebSocket dashboard
- [ ] Automated email alerts
- [ ] Custom date range filters
- [ ] Export to CSV/Excel
- [ ] Performance metrics (response times)

### Future
- [ ] A/B testing framework
- [ ] Predictive analytics
- [ ] AI-powered insights
- [ ] Mobile admin app
- [ ] Multi-admin roles

---

**Need Help?**
- 📖 Full documentation: `ADMIN_DASHBOARD_API.md`
- 📧 Email: cjalloh25@gmail.com
- 🐛 Issues: GitHub repo

**Last Updated**: December 16, 2025
