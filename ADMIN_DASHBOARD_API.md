# Base10 Admin Dashboard API

## Overview
The admin system provides comprehensive monitoring and management tools for the Base10 team to oversee application health, user activity, content quality, and system performance.

## Authentication
All admin endpoints require authentication with an admin account. Admin access is currently restricted to specific email addresses:

```python
ADMIN_EMAILS = [
    "cjalloh25@gmail.com",
    "esjallow03@gmail.com"
]
```

**Authorization**: Include JWT token in request headers:
```
Authorization: Bearer <your_jwt_token>
```

## Base URL
```
https://your-api.com/api/v1/admin
```

---

## 📊 Dashboard Endpoints

### 1. System Health
**GET** `/admin/health`

Get overall system health status and critical metrics.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-16T10:00:00Z",
  "database_connected": true,
  "redis_connected": true,
  "total_users": 1250,
  "active_users_24h": 420,
  "active_users_7d": 850,
  "total_questions": 700,
  "total_attempts": 85000,
  "average_accuracy": 68.5,
  "error_rate": 0.02
}
```

**Status Values:**
- `healthy` - All systems operational
- `degraded` - Some issues detected
- `critical` - Major problems requiring immediate attention

---

### 2. User Growth Metrics
**GET** `/admin/users/growth`

Track new registrations, retention rates, and churn.

**Response:**
```json
{
  "new_users_today": 45,
  "new_users_this_week": 312,
  "new_users_this_month": 1450,
  "retention_rate_7d": 62.5,
  "retention_rate_30d": 45.2,
  "churn_rate": 15.8,
  "average_session_duration_minutes": 22.5,
  "daily_active_users": 420,
  "monthly_active_users": 1850
}
```

**Key Metrics:**
- **Retention Rate (7d)**: % of users created 7 days ago who were active in last 24h
- **Retention Rate (30d)**: % of users created 30 days ago who were active in last 7 days
- **Churn Rate**: % of users inactive for >30 days

---

### 3. Content Quality
**GET** `/admin/content/quality`

Identify problematic questions that need review or removal.

**Response:**
```json
{
  "total_questions": 700,
  "questions_by_subject": {
    "MATHEMATICS": 180,
    "PHYSICS": 120,
    "CHEMISTRY": 110,
    "BIOLOGY": 100,
    "ENGLISH": 90,
    "ECONOMICS": 100
  },
  "questions_by_difficulty": {
    "EASY": 210,
    "MEDIUM": 350,
    "HARD": 140
  },
  "flagged_questions": 12,
  "low_quality_questions": 35,
  "high_quality_questions": 425,
  "total_reports": 156,
  "pending_reports": 18
}
```

**Quality Definitions:**
- **Flagged**: >3 user reports (needs immediate review)
- **Low Quality**: <40% accuracy (too hard or incorrect)
- **High Quality**: 60-80% accuracy (ideal difficulty)

---

### 4. Engagement Metrics
**GET** `/admin/engagement`

Track how actively users are engaging with the platform.

**Response:**
```json
{
  "total_attempts_today": 8500,
  "total_attempts_this_week": 58000,
  "average_attempts_per_user": 68.5,
  "average_study_time_minutes": 22.3,
  "users_with_streaks": 320,
  "longest_current_streak": 45,
  "questions_per_session": 15.2,
  "completion_rate": 68.5
}
```

**Key Insights:**
- **Completion Rate**: % of users who answered >10 questions
- **Study Streaks**: Consecutive days with activity
- **Session Metrics**: Average questions per study session

---

### 5. Top Users
**GET** `/admin/users/top?limit=10`

Identify power users for case studies, testimonials, or rewards.

**Query Parameters:**
- `limit` (optional): Number of users to return (default: 10, max: 100)

**Response:**
```json
[
  {
    "user_id": 123,
    "email": "topstudent@example.com",
    "phone_number": "+2207777777",
    "full_name": "John Doe",
    "total_attempts": 1250,
    "accuracy": 85.5,
    "study_streak": 45,
    "total_points": 15600,
    "level": 8,
    "last_active": "2025-12-16T09:30:00Z"
  }
]
```

**Use Cases:**
- Identify users for testimonials
- Reward top performers
- Analyze success patterns

---

### 6. Problematic Questions
**GET** `/admin/questions/problematic?min_attempts=50&max_accuracy=0.4&limit=20`

Get questions with low accuracy or multiple reports.

**Query Parameters:**
- `min_attempts` (optional): Minimum attempts to qualify (default: 50)
- `max_accuracy` (optional): Maximum accuracy rate (default: 0.4)
- `limit` (optional): Number of questions (default: 20, max: 100)

**Response:**
```json
[
  {
    "question_id": 456,
    "subject": "MATHEMATICS",
    "topic": "Quadratic Equations",
    "difficulty": "HARD",
    "accuracy_rate": 28.5,
    "total_attempts": 125,
    "report_count": 5,
    "reasons": ["INCORRECT_ANSWER", "UNCLEAR_WORDING"]
  }
]
```

**Action Items:**
- Review questions with <35% accuracy
- Investigate questions with >3 reports
- Fix or remove problematic content

---

### 7. Statistics Summary
**GET** `/admin/stats/summary?time_range=week`

Comprehensive dashboard with all key metrics in one call.

**Query Parameters:**
- `time_range` (optional): `today`, `week`, `month`, `all_time` (default: `week`)

**Response:**
```json
{
  "time_range": "week",
  "timestamp": "2025-12-16T10:00:00Z",
  "users": {
    "total": 1250,
    "verified": 1050,
    "verification_rate": 84.0,
    "active_in_period": 850
  },
  "activity": {
    "total_attempts": 58000,
    "average_accuracy": 68.5,
    "attempts_per_active_user": 68.2
  },
  "classrooms": {
    "total": 45,
    "total_teachers": 38,
    "avg_students_per_classroom": 18.9
  },
  "content": {
    "total_questions": 700,
    "total_flashcard_decks": 25,
    "pending_reports": 18
  }
}
```

---

## 👥 User Management

### 8. Search Users
**GET** `/admin/users/search?query=john&limit=10`

Search for users by email, phone, or name.

**Query Parameters:**
- `query` (required): Search term (min 3 characters)
- `limit` (optional): Results to return (default: 10, max: 50)

**Response:**
```json
[
  {
    "id": 123,
    "email": "john@example.com",
    "phone_number": "+2207777777",
    "full_name": "John Doe",
    "role": "student",
    "is_verified": true,
    "is_active": true,
    "created_at": "2025-11-01T10:00:00Z",
    "last_activity_date": "2025-12-16T09:30:00Z",
    "study_streak": 15,
    "total_points": 5600,
    "level": 5
  }
]
```

**Use Cases:**
- User support lookup
- Account verification
- Debugging user issues

---

### 9. Deactivate User
**PUT** `/admin/users/{user_id}/deactivate?reason=spam`

Deactivate a user account for abuse, spam, or user request.

**Path Parameters:**
- `user_id` (required): User ID to deactivate

**Query Parameters:**
- `reason` (required): Reason for deactivation

**Response:**
```json
{
  "message": "User deactivated successfully",
  "user_id": 123,
  "reason": "spam",
  "deactivated_by": "admin@base10.app",
  "timestamp": "2025-12-16T10:00:00Z"
}
```

---

### 10. Activate User
**PUT** `/admin/users/{user_id}/activate`

Reactivate a previously deactivated user account.

**Path Parameters:**
- `user_id` (required): User ID to activate

**Response:**
```json
{
  "message": "User activated successfully",
  "user_id": 123,
  "activated_by": "admin@base10.app",
  "timestamp": "2025-12-16T10:00:00Z"
}
```

---

## 📚 Content Management

### 11. Delete Question
**DELETE** `/admin/questions/{question_id}?reason=incorrect`

Delete a problematic question from the system.

**Path Parameters:**
- `question_id` (required): Question ID to delete

**Query Parameters:**
- `reason` (required): Reason for deletion

**Response:**
```json
{
  "message": "Question deleted successfully",
  "question_id": 456,
  "reason": "incorrect answer provided",
  "deleted_by": "admin@base10.app",
  "timestamp": "2025-12-16T10:00:00Z"
}
```

**⚠️ Warning**: This permanently removes the question and all associated attempts.

---

### 12. Resolve Report
**PUT** `/admin/reports/{report_id}/resolve?action=question_fixed`

Mark a question report as resolved after taking action.

**Path Parameters:**
- `report_id` (required): Report ID to resolve

**Query Parameters:**
- `action` (required): Action taken - `dismissed`, `question_fixed`, `question_deleted`
- `notes` (optional): Admin notes about the resolution

**Response:**
```json
{
  "message": "Report resolved successfully",
  "report_id": 789,
  "action": "question_fixed",
  "resolved_by": "admin@base10.app",
  "timestamp": "2025-12-16T10:00:00Z"
}
```

---

## 🚀 Usage Examples

### Monitor System Health (Python)
```python
import requests

BASE_URL = "https://your-api.com/api/v1"
headers = {
    "Authorization": "Bearer your_jwt_token"
}

# Get system health
response = requests.get(f"{BASE_URL}/admin/health", headers=headers)
health = response.json()

if health["status"] == "critical":
    print("🚨 ALERT: System is in critical state!")
    print(f"Active users (24h): {health['active_users_24h']}")
    print(f"Database connected: {health['database_connected']}")
    # Send alert to team
elif health["status"] == "healthy":
    print("✅ All systems operational")
```

### Check for Problematic Questions (Python)
```python
# Get questions needing review
response = requests.get(
    f"{BASE_URL}/admin/questions/problematic",
    params={
        "min_attempts": 50,
        "max_accuracy": 0.35,
        "limit": 20
    },
    headers=headers
)

problems = response.json()

for q in problems:
    print(f"Question {q['question_id']} ({q['subject']} - {q['topic']})")
    print(f"  Accuracy: {q['accuracy_rate']}%")
    print(f"  Reports: {q['report_count']}")
    print(f"  Reasons: {', '.join(q['reasons'])}")
    print()
```

### Monitor User Growth (JavaScript)
```javascript
const BASE_URL = "https://your-api.com/api/v1";
const headers = {
  "Authorization": "Bearer your_jwt_token"
};

async function checkGrowth() {
  const response = await fetch(`${BASE_URL}/admin/users/growth`, { headers });
  const growth = await response.json();
  
  console.log(`📈 Growth Metrics:`);
  console.log(`  New users today: ${growth.new_users_today}`);
  console.log(`  New users this week: ${growth.new_users_this_week}`);
  console.log(`  7-day retention: ${growth.retention_rate_7d}%`);
  console.log(`  Churn rate: ${growth.churn_rate}%`);
  
  // Alert if churn is high
  if (growth.churn_rate > 25) {
    alert("⚠️ High churn rate detected!");
  }
}
```

### Search and Manage Users (cURL)
```bash
# Search for users
curl -X GET "https://your-api.com/api/v1/admin/users/search?query=john&limit=10" \
  -H "Authorization: Bearer your_jwt_token"

# Deactivate a user
curl -X PUT "https://your-api.com/api/v1/admin/users/123/deactivate?reason=spam" \
  -H "Authorization: Bearer your_jwt_token"

# Reactivate a user
curl -X PUT "https://your-api.com/api/v1/admin/users/123/activate" \
  -H "Authorization: Bearer your_jwt_token"
```

---

## 📊 Monitoring Best Practices

### Daily Checks
1. **System Health** - Check status is "healthy"
2. **Active Users** - Monitor 24h active user count
3. **Error Rate** - Ensure <1% error rate
4. **Pending Reports** - Review and resolve user reports

### Weekly Analysis
1. **User Growth** - Track new registrations and retention
2. **Engagement Metrics** - Monitor study time and completion rates
3. **Content Quality** - Review problematic questions
4. **Top Users** - Identify power users for case studies

### Monthly Review
1. **Churn Rate** - Analyze inactive users
2. **Content Gaps** - Identify missing subjects/topics
3. **Performance Trends** - Compare month-over-month growth
4. **Feature Usage** - Track classroom, flashcard adoption

---

## 🔐 Security Considerations

### Admin Access Control
- Only specific email addresses have admin access
- All admin actions should be logged (TODO: implement audit log)
- Use strong JWT tokens with reasonable expiration
- Monitor for suspicious admin activity

### Data Privacy
- User searches return minimal PII
- Deactivation requires justification
- Deletions should be auditable
- Consider GDPR compliance for European users

---

## 🚀 Future Enhancements

### Phase 2: Advanced Analytics
- [ ] Real-time dashboard with WebSocket updates
- [ ] Custom date range filters
- [ ] Export data to CSV/Excel
- [ ] Automated alerts (email/Slack)
- [ ] Performance metrics (response times, slow queries)

### Phase 3: Content Management
- [ ] Bulk question import/export
- [ ] Question editor UI
- [ ] A/B testing for content
- [ ] Automated quality scoring
- [ ] AI-powered content suggestions

### Phase 4: User Management
- [ ] Bulk user operations
- [ ] Role-based admin permissions
- [ ] Audit log for all admin actions
- [ ] User communication tools (send emails/notifications)
- [ ] Account merge/split tools

---

## 📝 Notes

### Current Limitations
1. Admin access hardcoded to specific emails (TODO: add is_admin field to User model)
2. No audit logging (all actions should be logged)
3. No rate limiting on admin endpoints
4. Error tracking not implemented (error_rate always 0)
5. Performance metrics not collected

### Recommended Monitoring Tools
- **Uptime**: UptimeRobot or Pingdom
- **Error Tracking**: Sentry
- **Analytics**: PostHog or Mixpanel
- **Logs**: Better Stack or Papertrail
- **Alerts**: PagerDuty or Opsgenie

---

**Last Updated**: December 16, 2025
**API Version**: 1.0.0
**Status**: ✅ Deployed to production
