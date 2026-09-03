# Email Service & User Onboarding Integration

## Overview
Base10 now uses **Resend** for transactional emails with role-based onboarding flows for students, teachers, and parents.

## 🚀 Quick Setup

### 1. Install Resend
```bash
pip install resend
```

### 2. Configure Environment Variables
Add to your `.env` file:
```bash
RESEND_API_KEY=re_your_api_key_here
RESEND_FROM_EMAIL="Base10 <noreply@yourdomain.com>"
FRONTEND_URL=http://localhost:3000
```

### 3. Run Database Migration
```bash
alembic upgrade head
```

This adds the following fields to the `users` table:
- `verification_token` - Secure token for email verification
- `verification_token_expires` - Token expiration (24 hours)
- `verified_at` - Timestamp when email was verified
- `role` - User role (student, teacher, parent)
- `username` - Alternative login identifier

## 📧 Email Templates

### Welcome Email
Sent immediately after registration with email verification link.

**Role-Specific Content:**
- **Students**: 3-step onboarding (verify → complete profile → first quiz)
- **Teachers**: Classroom setup guide (verify → create classroom → invite students)
- **Parents**: Child monitoring setup (verify → link account → set preferences)

**Features:**
- Beautiful HTML design with gradient headers
- Responsive mobile layout
- Clear call-to-action buttons
- Platform features overview

### Verification Email
Sent when user requests re-verification or clicks "resend verification".

**Features:**
- 24-hour token expiration
- Security notice for unauthorized requests
- Fallback plain text link

### Password Reset Email
Sent when user requests password reset.

**Features:**
- 1-hour secure token expiration
- Security warning banner
- Clear reset instructions

### Weekly Progress Report
Automated weekly email for students.

**Features:**
- Questions answered count
- Accuracy percentage
- Study minutes tracked
- Top subjects & improvement areas
- Dashboard link

### Teacher Classroom Creation
Sent when teacher creates a new classroom.

**Features:**
- Large, easy-to-share classroom code
- Student join instructions
- WhatsApp/SMS sharing tips

### Parent Weekly Summary
Weekly report for parents monitoring their children.

**Features:**
- Child's study time & questions attempted
- Overall accuracy with week-over-week change
- Strongest subjects & areas needing attention
- Actionable recommendations

## 🔄 Onboarding Flows

### Student Onboarding
```
Registration → Welcome Email (with verification link)
    ↓
Email Verification → Post-Verification Guidance
    ↓
Complete Profile → First Practice Quiz
```

### Teacher Onboarding
```
Registration → Welcome Email (with verification link)
    ↓
Email Verification → Classroom Setup Guide
    ↓
Create Classroom → Classroom Created Email (with invite code)
    ↓
Invite Students → Student Join Notifications
```

### Parent Onboarding
```
Registration → Welcome Email (with verification link)
    ↓
Email Verification → Child Linking Instructions
    ↓
Link to Child Account → Weekly Progress Reports
```

## 🔌 API Endpoints

### Registration with Email
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "student@example.com",
  "password": "securepass123",
  "full_name": "John Doe",
  "role": "student"  // optional, defaults to "student"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "student@example.com",
    "full_name": "John Doe",
    "role": "student",
    "is_verified": false
  }
}
```

**Side Effect:** Welcome email sent in background (non-blocking).

### Email Verification
```http
GET /api/v1/auth/verify-email?token=abc123xyz
```

**Response:**
```json
{
  "message": "Email verified successfully! Welcome to Base10.",
  "user_id": 1,
  "verified_at": "2025-12-16T10:30:00Z"
}
```

**Side Effect:** Post-verification guidance email sent with next steps.

### Resend Verification Email
```http
POST /api/v1/auth/resend-verification
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Verification email sent successfully"
}
```

## 🛠️ Services Architecture

### OnboardingService
`app/services/onboarding_service.py`

**Methods:**
- `send_welcome_email(user)` - Send role-specific welcome email
- `send_verification_reminder(user)` - Resend verification email
- `verify_email(token)` - Verify email with token
- `send_classroom_created_email(teacher, classroom_name, invite_code)` - Teacher classroom creation

### CommunicationService
`app/services/comms_service.py`

**Updated Methods:**
- `_send_email(email, subject, body, html=None)` - Now uses Resend instead of SendGrid

**Features:**
- HTML email support (falls back to plain text)
- Automatic error logging
- Integration with priority-based notification routing

### Email Templates
`app/services/email_templates.py`

**Functions:**
- `get_welcome_email(user_name, user_role, verification_url)`
- `get_verification_email(user_name, verification_url)`
- `get_password_reset_email(user_name, reset_url)`
- `get_weekly_report_email(user_name, stats)`
- `get_teacher_classroom_invite_email(teacher_name, classroom_name, invite_code)`
- `get_parent_weekly_summary_email(parent_name, student_name, stats)`

## 🔒 Security

### Token Generation
- Uses Python's `secrets.token_urlsafe(32)` for cryptographically secure tokens
- 24-hour expiration for email verification
- 1-hour expiration for password resets

### Email Verification Flow
1. User registers → `verification_token` generated and stored
2. Token sent in email link: `https://frontend.com/verify-email?token=xyz`
3. User clicks link → backend validates token & expiration
4. Token cleared after successful verification
5. `is_verified` set to `True`, `verified_at` timestamp recorded

## 📊 Monitoring & Logging

### Email Logging
```python
logger.info(f"📧 Email sent successfully to {email}: {subject} (ID: {response_id})")
logger.error(f"❌ Email failed to {email}: {error}")
```

### Onboarding Tracking
```python
logger.info(f"✅ Welcome email sent to {user.email} (role: {user.role})")
logger.info(f"✅ Email verified for user {user.email}")
```

## 🧪 Testing

### Manual Testing
```bash
# 1. Register a user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User",
    "role": "student"
  }'

# 2. Check your email inbox for welcome email

# 3. Click verification link in email (or use token manually)
curl -X GET "http://localhost:8000/api/v1/auth/verify-email?token=YOUR_TOKEN"

# 4. Check for post-verification guidance email
```

### Automated Testing
```python
# tests/test_onboarding.py
async def test_welcome_email_sent_on_registration():
    # Register user
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "testpass",
        "role": "student"
    })
    
    assert response.status_code == 201
    # Check that email was queued (mock Resend in tests)
```

## 🎨 Email Design

All emails feature:
- **Brand Colors**: Purple gradient (#667eea → #764ba2)
- **Responsive Design**: Mobile-optimized with max-width 600px
- **Clear CTAs**: Large buttons for primary actions
- **Accessible**: Proper HTML structure, fallback text links
- **Professional**: Clean typography, proper spacing, footer with unsubscribe

## 🚦 Production Checklist

- [ ] Set `RESEND_API_KEY` in production environment
- [ ] Update `RESEND_FROM_EMAIL` to use verified domain
- [ ] Set `FRONTEND_URL` to production URL
- [ ] Run database migration: `alembic upgrade head`
- [ ] Test email delivery in production
- [ ] Verify email links work with production URLs
- [ ] Set up SPF/DKIM records for email domain
- [ ] Monitor Resend dashboard for delivery metrics
- [ ] Set up email templates in Resend dashboard (optional)

## 📈 Future Enhancements

### Phase 2
- [ ] Email template builder in admin panel
- [ ] A/B testing for onboarding emails
- [ ] Email preferences management (frequency, types)
- [ ] Rich analytics tracking (open rates, click rates)
- [ ] Scheduled digest emails (daily/weekly reports)

### Phase 3
- [ ] Transactional email history in user profile
- [ ] Email bounce handling & list hygiene
- [ ] Multi-language email templates
- [ ] Advanced segmentation for targeted campaigns

## 📚 Resources

- [Resend Documentation](https://resend.com/docs)
- [Resend Python SDK](https://github.com/resendlabs/resend-python)
- [Email Best Practices](https://resend.com/docs/best-practices)
- [Transactional Email Guide](https://resend.com/docs/send-with-python)

## 🆘 Troubleshooting

### Email Not Sending
1. Check `RESEND_API_KEY` is set correctly
2. Verify domain is verified in Resend dashboard
3. Check logs for error messages
4. Test with Resend API directly

### Verification Link Not Working
1. Check token expiration (24 hours)
2. Verify `FRONTEND_URL` is correct
3. Check user's `verification_token` in database
4. Ensure token hasn't been cleared

### User Not Receiving Email
1. Check spam/junk folder
2. Verify email address is correct
3. Check Resend dashboard for delivery status
4. Test with different email provider (Gmail, Outlook, etc.)

## 💡 Tips

1. **Test with Real Emails**: Use real email addresses in development to see actual rendering
2. **Check Mobile**: Test emails on mobile devices for responsive design
3. **Monitor Logs**: Watch application logs during registration to see email sending status
4. **Use Resend Sandbox**: Test mode available for development without counting against quota
5. **Customize Templates**: Modify `email_templates.py` to match your brand voice
