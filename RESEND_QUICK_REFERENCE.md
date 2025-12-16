# 🚀 Resend Email Service - Quick Reference

## ⚡ 60-Second Setup

```bash
# 1. Install & Configure
pip install resend
echo 'RESEND_API_KEY=re_your_key' >> .env
echo 'RESEND_FROM_EMAIL="Base10 <noreply@yourdomain.com>"' >> .env
echo 'FRONTEND_URL=http://localhost:3000' >> .env

# 2. Migrate Database
alembic upgrade head

# 3. Start Server
uvicorn app.main:app --reload
```

## 📬 Email Types

| Email | Trigger | Recipient | When |
|-------|---------|-----------|------|
| Welcome | Registration | All users | Immediately |
| Verification | Registration/Resend | All users | On demand |
| Password Reset | Forgot password | User requesting | On demand |
| Weekly Report | Automated | Students | Every Sunday |
| Classroom Created | Teacher creates class | Teacher | Immediately |
| Parent Summary | Automated | Parents | Every Sunday |

## 🔌 API Endpoints

```http
# Register with email
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "pass123",
  "full_name": "John Doe",
  "role": "student"  // or "teacher", "parent"
}

# Verify email
GET /api/v1/auth/verify-email?token=abc123

# Resend verification
POST /api/v1/auth/resend-verification
Authorization: Bearer <jwt_token>
```

## 🎨 Email Template Functions

```python
from app.services.email_templates import (
    get_welcome_email,              # Registration welcome
    get_verification_email,         # Email verification
    get_password_reset_email,       # Password reset
    get_weekly_report_email,        # Student progress
    get_teacher_classroom_invite_email,  # Classroom setup
    get_parent_weekly_summary_email      # Parent reports
)
```

## 🔧 Onboarding Service Usage

```python
from app.services.onboarding_service import OnboardingService

# Initialize
service = OnboardingService(db)

# Send welcome email
await service.send_welcome_email(user)

# Verify email
verified_user = await service.verify_email(token)

# Resend verification
await service.send_verification_reminder(user)

# Classroom creation email
await service.send_classroom_created_email(teacher, "Class A", "ABC123")
```

## 📊 User Model Fields

```python
user.verification_token          # "xyz123..." or None
user.verification_token_expires  # DateTime (24h from creation)
user.verified_at                 # DateTime or None
user.is_verified                 # Boolean (True/False)
user.role                        # "student", "teacher", or "parent"
user.username                    # Alternative login
```

## 🔒 Security Tokens

```python
# Token generation (automatic)
secrets.token_urlsafe(32)  # 256-bit secure token

# Expiration times
Email Verification: 24 hours
Password Reset: 1 hour (when implemented)
```

## 📈 Log Messages

```bash
# Success indicators
📧 Email sent successfully to user@example.com: Welcome to Base10 (ID: abc)
✅ Welcome email sent to user@example.com (role: student)
✅ Email verified for user user@example.com

# Error indicators
❌ Email failed to user@example.com: Invalid API key
❌ Failed to send welcome email: Connection timeout
```

## 🧪 Quick Test

```bash
# Test registration
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123","role":"student"}'

# Check logs for email confirmation
# Look for: ✅ Welcome email sent to test@test.com
```

## 🚨 Common Issues

| Issue | Solution |
|-------|----------|
| Import error | Run `pip install resend` |
| Invalid API key | Check `RESEND_API_KEY` in `.env` |
| Email not received | Check spam folder, Resend dashboard |
| Token expired | Use `/resend-verification` endpoint |
| Domain not verified | Use `onboarding@resend.dev` in dev |

## 📚 Documentation Files

- `EMAIL_ONBOARDING_GUIDE.md` - Complete integration guide
- `RESEND_INTEGRATION_SUMMARY.md` - Detailed summary
- `.env.example` - Configuration template
- `setup_email_service.sh` - Automated setup script

## 🎯 Environment Variables (Required)

```bash
RESEND_API_KEY=re_xxxxx          # Get from resend.com
RESEND_FROM_EMAIL="Base10 <noreply@yourdomain.com>"
FRONTEND_URL=http://localhost:3000
```

## 🔄 Onboarding Flows

**Student:**
Register → Welcome Email → Verify → Profile Setup → First Quiz

**Teacher:**
Register → Welcome Email → Verify → Create Classroom → Invite Students

**Parent:**
Register → Welcome Email → Verify → Link Child → Weekly Reports

## 💾 Database Migration

```bash
# Upgrade to latest
alembic upgrade head

# Check current version
alembic current

# Rollback if needed
alembic downgrade -1
```

## 🎨 Email Design Colors

```css
Primary: #667eea (Purple)
Secondary: #764ba2 (Dark Purple)
Success: #28a745 (Green)
Warning: #ffc107 (Yellow)
Danger: #dc3545 (Red)
Info: #17a2b8 (Cyan)
```

## ⚙️ Production Checklist

- [ ] Get Resend API key
- [ ] Verify domain in Resend
- [ ] Set up SPF/DKIM DNS records
- [ ] Update `RESEND_FROM_EMAIL` with verified domain
- [ ] Set production `FRONTEND_URL`
- [ ] Run migrations
- [ ] Test email delivery
- [ ] Monitor Resend dashboard

## 🌐 Useful Links

- [Resend Dashboard](https://resend.com/dashboard)
- [API Docs](https://resend.com/docs)
- [Python SDK](https://github.com/resendlabs/resend-python)
- [Verify Domain](https://resend.com/domains)

---

**Need Help?** Read `EMAIL_ONBOARDING_GUIDE.md` for full documentation!
