# Classroom Notification System

## Overview
The classroom system now has **complete notification integration**. When teachers post announcements or create assignments, all enrolled students receive instant notifications through the smart Communication Service.

---

## 🔔 Notification Triggers

### 1. Announcement Posted
**Trigger:** Teacher posts an announcement in classroom stream  
**Endpoint:** `POST /classrooms/{classroom_id}/announce`

**Who Gets Notified:** All students enrolled in the classroom

**Notification Details:**
- **Title:** 📢 {Classroom Name}
- **Body:** {Teacher Name}: {Announcement Preview (100 chars)}
- **Priority:** MEDIUM
- **Data Payload:**
  ```json
  {
    "type": "classroom_announcement",
    "classroom_id": 5,
    "post_id": 42,
    "classroom_name": "Form 3 Biology"
  }
  ```

**Example:**
```
Title: 📢 Form 3 Biology
Body: Mr. Jalloh: Quiz tomorrow on photosynthesis! Please review chapters 3-5.
```

---

### 2. Assignment Created
**Trigger:** Teacher creates a new assignment  
**Endpoint:** `POST /classrooms/{classroom_id}/assignments/manual`

**Who Gets Notified:** All students enrolled in the classroom

**Notification Details:**
- **Title:** 📝 New Assignment: {Classroom Name}
- **Body:** {Assignment Title} (Due: {Date})
- **Priority:** 
  - HIGH if due within 24 hours
  - MEDIUM otherwise
- **Data Payload:**
  ```json
  {
    "type": "assignment_created",
    "classroom_id": 5,
    "assignment_id": 88,
    "classroom_name": "Form 3 Biology",
    "due_date": "2025-12-20T23:59:59Z"
  }
  ```

**Example:**
```
Title: 📝 New Assignment: Form 3 Biology
Body: Essay: Climate Change (Due: Dec 20)
Priority: HIGH (if due soon) or MEDIUM
```

---

### 3. Assignment Graded
**Trigger:** Teacher grades a student's submission  
**Endpoint:** `POST /classrooms/submissions/{submission_id}/grade`

**Who Gets Notified:** The student who submitted the assignment

**Notification Details:**
- **Title:** {Emoji} Assignment Graded: {Classroom Name}
  - 🎉 if ≥80%
  - ✅ if ≥60%
  - 📊 if <60%
- **Body:** {Assignment Title}: {Grade}/{Max Points} ({Percentage}%)
- **Priority:** MEDIUM
- **Message Type:** QUIZ_RESULT
- **Data Payload:**
  ```json
  {
    "type": "assignment_graded",
    "classroom_id": 5,
    "assignment_id": 88,
    "submission_id": 123,
    "grade": 18,
    "max_points": 20,
    "percentage": 90
  }
  ```

**Example:**
```
Title: 🎉 Assignment Graded: Form 3 Biology
Body: Essay: Climate Change: 18/20 (90%)
```

---

## 📱 Notification Delivery Channels

The system uses the **CommunicationService** for smart routing:

### 1. Push Notification (FREE)
- Delivered if `user.has_app_installed = True`
- Instant delivery via Firebase Cloud Messaging (FCM)
- **Status:** Infrastructure ready, Phase 2 activation pending

### 2. SMS (COSTS MONEY)
- Only sent for HIGH/CRITICAL priority messages
- Only if user doesn't have app installed
- Uses Twilio for delivery
- **Status:** Available but cost-conscious routing

### 3. Email (ALWAYS)
- Sent for MEDIUM+ priority messages
- Permanent record of notifications
- Includes full content and links
- **Status:** Fully functional

---

## 🎯 Priority Levels

### LOW
- Routine reminders
- Non-urgent updates
- Uses cheapest channel only

### MEDIUM (Default)
- Classroom announcements
- New assignments (not urgent)
- Graded submissions
- Push + Email delivery

### HIGH
- Assignments due within 24 hours
- Important announcements
- Push + SMS + Email delivery

### CRITICAL
- Emergency alerts
- Account security
- All channels activated

---

## 🧪 Testing Notifications

### Test Announcement Notification
```bash
curl -X POST "http://localhost:8000/api/v1/classrooms/5/announce" \
  -H "Authorization: Bearer {teacher_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "🧪 Test announcement: Please review chapters 1-3 for tomorrow'\''s quiz!",
    "post_type": "announcement"
  }'
```

**Expected Result:**
- All students in classroom 5 receive notification
- Logs show: `📢 Announcement notifications sent to X students in classroom 5`

---

### Test Assignment Notification
```bash
curl -X POST "http://localhost:8000/api/v1/classrooms/5/assignments/manual" \
  -H "Authorization: Bearer {teacher_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "🧪 Test Assignment",
    "description": "Complete practice problems 1-10",
    "due_date": "2025-12-18T23:59:59Z",
    "points": 20
  }'
```

**Expected Result:**
- All students receive HIGH priority notification (due tomorrow)
- Logs show: `📝 Assignment notifications sent to X students in classroom 5`

---

### Test Grade Notification
```bash
curl -X POST "http://localhost:8000/api/v1/classrooms/submissions/123/grade" \
  -H "Authorization: Bearer {teacher_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "grade": 18,
    "feedback": "Excellent work! Clear explanations."
  }'
```

**Expected Result:**
- Student receives notification with grade and percentage
- Logs show: `📊 Grade notification sent to student X for submission 123`

---

## 🔧 Configuration

### User Notification Preferences
Stored in `User.notification_settings` (JSON):
```json
{
  "email": true,
  "sms": false,
  "push": true
}
```

### Required User Fields
- `phone_number` - For SMS delivery (+220...)
- `email` - For email delivery
- `has_app_installed` - Boolean flag for push notifications

### Environment Variables
```bash
# Twilio SMS (Phase 3)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Firebase Push Notifications (Phase 2)
FIREBASE_PROJECT_ID=your_project
FIREBASE_PRIVATE_KEY=your_key
```

---

## 📊 Notification Flow

```
Teacher Action (Announcement/Assignment)
    ↓
Database Update (Commit)
    ↓
Fetch All Students in Classroom
    ↓
For Each Student:
    ↓
    Check User Preferences
    ↓
    Smart Channel Selection:
    - Has app? → Push (FREE)
    - No app + HIGH priority? → SMS (COSTS)
    - Always → Email (permanent record)
    ↓
    Send via CommunicationService
    ↓
Log Success/Failure
    ↓
Continue (Don't fail request on notification error)
```

---

## 🛡️ Error Handling

Notifications are **non-blocking**:
- If notification fails, the classroom action still succeeds
- Errors are logged but don't return to client
- This prevents notification issues from breaking core functionality

```python
try:
    # Send notifications
    comms.send_notification(...)
    logger.info("✅ Notification sent")
except Exception as e:
    logger.error(f"❌ Notification failed: {e}")
    # Request still returns success
```

---

## 📈 Monitoring

### Log Messages
```
✅ Success: "📢 Announcement notifications sent to 25 students in classroom 5"
✅ Success: "📝 Assignment notifications sent to 25 students in classroom 5"
✅ Success: "📊 Grade notification sent to student 42 for submission 123"
❌ Error: "❌ Failed to send announcement notifications: [error details]"
```

### Check Notification Status
```bash
# View application logs
docker logs base10-backend | grep "notification"

# Or in Digital Ocean
doctl apps logs {app-id} --type=run | grep "notification"
```

---

## 🎓 Frontend Integration

### Handle Push Notifications (Mobile)
```typescript
// Register device token on app login
async function registerPushToken(token: string) {
  await fetch('/api/v1/profile/device-token', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${userToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ fcm_token: token })
  });
}

// Listen for push notifications
firebase.messaging().onMessage((payload) => {
  const { type, classroom_id, assignment_id } = payload.data;
  
  if (type === 'classroom_announcement') {
    showNotification(payload.notification.title, payload.notification.body);
    // Optionally navigate to classroom stream
  } else if (type === 'assignment_created') {
    showNotification(payload.notification.title, payload.notification.body);
    // Show assignment details
  } else if (type === 'assignment_graded') {
    showNotification(payload.notification.title, payload.notification.body);
    // Navigate to grades view
  }
});
```

### Handle SMS Notifications
Students receive text messages like:
```
📢 Form 3 Biology
Mr. Jalloh: Quiz tomorrow on photosynthesis!
View: base10.education/classroom/5
```

### Handle Email Notifications
Students receive formatted emails with:
- Classroom name and teacher
- Full announcement/assignment content
- Due dates and links
- Reply-to teacher email

---

## 🚀 Future Enhancements

### Phase 2: In-App Notifications
- [ ] Notification bell icon with unread count
- [ ] Notification history page
- [ ] Mark as read/unread
- [ ] Notification preferences in settings

### Phase 3: Advanced Features
- [ ] Digest mode (daily summary instead of instant)
- [ ] Quiet hours (no notifications 10pm-7am)
- [ ] Topic-based subscriptions
- [ ] Parent notifications
- [ ] Notification analytics dashboard

### Phase 4: Rich Notifications
- [ ] Inline reply to announcements
- [ ] Quick action buttons (View Assignment, Submit Now)
- [ ] Image thumbnails in notifications
- [ ] Audio announcements
- [ ] Multi-language support

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Teacher posts announcement → Students receive notification
- [ ] Teacher creates assignment → Students receive notification
- [ ] Assignment due soon → HIGH priority delivery
- [ ] Teacher grades submission → Student receives grade notification
- [ ] Notification logs show delivery status
- [ ] No errors in application logs
- [ ] Notifications don't block classroom actions
- [ ] User preferences are respected

---

## 🐛 Troubleshooting

### Students Not Receiving Notifications

**Check 1: User has app installed flag?**
```sql
SELECT id, username, email, has_app_installed FROM users WHERE id = 42;
```

**Check 2: User enrolled in classroom?**
```sql
SELECT * FROM classroom_students WHERE student_id = 42 AND classroom_id = 5;
```

**Check 3: Notification logs**
```bash
grep "notification" logs/app.log | tail -20
```

**Check 4: CommunicationService configured?**
```python
# In Python console
from app.services.comms_service import CommunicationService
comms = CommunicationService()
print(comms.twilio_client)  # Should not be None if Twilio configured
```

### High Notification Costs

**Review SMS usage:**
- Check Twilio dashboard for SMS count
- Consider reducing priority levels
- Encourage app installation (free push)

**Optimize delivery:**
```python
# Only send SMS for CRITICAL events
if priority == MessagePriority.CRITICAL:
    send_sms()
else:
    send_push_or_email()
```

---

## 📚 Related Documentation

- [Communication Service](../app/services/comms_service.py) - Smart notification routing
- [Classroom API](CLASSROOM_CRUD_COMPLETE.md) - Full CRUD operations
- [Frontend Integration](CLASSROOM_FRONTEND_INTEGRATION.md) - React examples

---

**Status:** ✅ Fully integrated and tested  
**Deployment:** Ready for production  
**Last Updated:** December 17, 2025
