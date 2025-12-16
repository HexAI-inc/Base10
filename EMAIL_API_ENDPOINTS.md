# Base10 Email API Endpoints Documentation

## Authentication Endpoints with Email Integration

### 1. Register User (Sends Welcome Email)

**Endpoint:** `POST /api/v1/auth/register`

**Description:** Creates a new user account and automatically sends a role-specific welcome email with email verification link in the background.

**Request Body:**
```json
{
  "email": "student@example.com",
  "password": "securePass123!",
  "full_name": "John Doe",
  "username": "johndoe",           // Optional
  "phone_number": "+1234567890",   // Optional (for SMS-only users)
  "role": "student"                // Optional: "student" (default), "teacher", "parent"
}
```

**Response:** `201 Created`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 123,
    "email": "student@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "phone_number": null,
    "role": "student",
    "is_active": true,
    "is_verified": false,
    "created_at": "2025-12-16T10:30:00Z"
  }
}
```

**Side Effects:**
- Creates user in database
- Generates 7-day JWT token for offline-first usage
- **Sends welcome email in background** (non-blocking)
- Email includes:
  - Role-specific onboarding content
  - Email verification link with 24-hour token
  - Feature overview and next steps

**Email Template Used:**
- `get_welcome_email(user_name, user_role, verification_url)`

**Error Responses:**
```json
// 400 Bad Request - Email already registered
{
  "detail": "Email already registered"
}

// 400 Bad Request - Phone already registered
{
  "detail": "Phone number already registered"
}

// 422 Validation Error - Missing required fields
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Either email or phone_number must be provided",
      "type": "value_error"
    }
  ]
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "testpass123",
    "full_name": "Test Student",
    "role": "student"
  }'
```

---

### 2. Verify Email

**Endpoint:** `GET /api/v1/auth/verify-email`

**Description:** Verifies user's email address using the token sent in the welcome email. Marks user as verified and sends post-verification guidance email.

**Query Parameters:**
- `token` (required): The verification token from the email link

**Request:**
```
GET /api/v1/auth/verify-email?token=XyZ123AbC456DeF789...
```

**Response:** `200 OK`
```json
{
  "message": "Email verified successfully! Welcome to Base10.",
  "user_id": 123,
  "verified_at": "2025-12-16T11:00:00Z"
}
```

**Side Effects:**
- Sets `user.is_verified = True`
- Records `verified_at` timestamp
- Clears `verification_token` and `verification_token_expires`
- **Sends post-verification guidance email** with role-specific next steps

**Email Template Used:**
- `_format_guidance_html(user, guidance)` - Role-specific guidance

**Error Responses:**
```json
// 400 Bad Request - Invalid or expired token
{
  "detail": "Invalid or expired verification token"
}
```

**Token Validation:**
- Must match a user's `verification_token` in database
- Must not be expired (24 hours from generation)
- Token is single-use (cleared after verification)

**Example cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/auth/verify-email?token=XyZ123AbC456"
```

**Example Frontend Integration:**
```javascript
// User clicks verification link in email
// https://app.base10.com/verify-email?token=XyZ123AbC456

// Frontend extracts token and calls API
const urlParams = new URLSearchParams(window.location.search);
const token = urlParams.get('token');

fetch(`/api/v1/auth/verify-email?token=${token}`)
  .then(res => res.json())
  .then(data => {
    console.log(data.message); // "Email verified successfully!"
    // Redirect to dashboard or show success message
  })
  .catch(err => {
    // Show error: invalid or expired token
  });
```

---

### 3. Resend Verification Email

**Endpoint:** `POST /api/v1/auth/resend-verification`

**Description:** Resends the email verification link to the authenticated user. Only works for unverified users.

**Authentication:** Required (Bearer token)

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

**Request Body:** None

**Response:** `200 OK`
```json
{
  "message": "Verification email sent successfully"
}
```

**Side Effects:**
- Generates new verification token (invalidates old token)
- Updates `verification_token_expires` to 24 hours from now
- **Sends verification reminder email**

**Email Template Used:**
- `get_verification_email(user_name, verification_url)`

**Error Responses:**
```json
// 400 Bad Request - Already verified
{
  "detail": "Email already verified"
}

// 400 Bad Request - No email address
{
  "detail": "No email address associated with account"
}

// 401 Unauthorized - Invalid/missing token
{
  "detail": "Could not validate credentials"
}

// 500 Internal Server Error - Email send failed
{
  "detail": "Failed to send verification email"
}
```

**Rate Limiting:** No rate limiting currently implemented (consider adding in production)

**Example cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/resend-verification \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json"
```

**Example JavaScript:**
```javascript
// User clicks "Resend verification email" button
fetch('/api/v1/auth/resend-verification', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${userToken}`,
    'Content-Type': 'application/json'
  }
})
  .then(res => res.json())
  .then(data => {
    alert('Verification email sent! Check your inbox.');
  })
  .catch(err => {
    console.error('Failed to resend:', err);
  });
```

---

## Email Flow Diagrams

### Registration Flow
```
User submits registration form
    ↓
POST /api/v1/auth/register
    ↓
User created in database (is_verified: false)
    ↓
JWT token returned immediately
    ↓
Background task: OnboardingService.send_welcome_email()
    ├─ Generate verification token
    ├─ Store in database (expires in 24h)
    ├─ Build verification URL
    ├─ Render HTML email template
    └─ Send via Resend API
    ↓
User receives welcome email
```

### Verification Flow
```
User opens email
    ↓
Clicks "Verify Email" button
    ↓
Redirects to: https://app.base10.com/verify-email?token=xyz
    ↓
Frontend extracts token
    ↓
GET /api/v1/auth/verify-email?token=xyz
    ↓
Backend validates token:
    ├─ Find user by token
    ├─ Check expiration
    └─ Verify not already used
    ↓
If valid:
    ├─ Set is_verified = true
    ├─ Set verified_at timestamp
    ├─ Clear verification_token
    └─ Send post-verification guidance email
    ↓
Return success response
    ↓
Frontend shows success message & redirects to dashboard
```

### Resend Flow
```
User on dashboard, sees "Email not verified" banner
    ↓
Clicks "Resend verification email"
    ↓
POST /api/v1/auth/resend-verification (with Bearer token)
    ↓
Backend checks:
    ├─ User authenticated?
    ├─ User not already verified?
    └─ User has email address?
    ↓
If valid:
    ├─ Generate NEW verification token
    ├─ Update database
    └─ Send verification reminder email
    ↓
Return success response
    ↓
Frontend shows "Email sent!" message
```

---

## Email Templates

### 1. Welcome Email (Role-Specific)

**Function:** `get_welcome_email(user_name, user_role, verification_url)`

**Variants:**
- **Student**: Focus on practice questions, progress tracking, first quiz
- **Teacher**: Focus on classroom creation, student management, analytics
- **Parent**: Focus on child monitoring, progress reports, linking accounts

**Content:**
- Purple gradient header with "Base10" branding
- Personalized greeting: "Hi {user_name},"
- Role-specific title and message
- 3-step onboarding checklist
- Large "Verify Your Email" CTA button
- Feature overview (700+ questions, analytics, AI, offline-first)
- Footer with support links

**HTML Features:**
- Mobile-responsive (max-width: 600px)
- Inline CSS for email client compatibility
- Fallback plain text link
- Professional typography

---

### 2. Verification Reminder

**Function:** `get_verification_email(user_name, verification_url)`

**Content:**
- Simplified design focused on one action
- "Verify Your Email" heading
- Brief explanation
- Large "Verify Email Address" button
- Plain text link fallback
- Expiration notice (24 hours)
- Security note (ignore if not you)

**Use Cases:**
- User clicks "Resend verification"
- Original email lost/deleted
- Token expired

---

### 3. Post-Verification Guidance

**Function:** `_format_guidance_html(user, guidance)`

**Content:**
- "✅ Email Verified!" header
- Role-specific next steps
- Detailed instructions for profile completion
- "Go to Dashboard" CTA button

**Variants:**
- **Student**: Complete profile → Take first quiz → Track progress
- **Teacher**: Create classroom → Invite students → View analytics
- **Parent**: Link child account → Set preferences → Weekly reports

---

## Testing

### Test Registration + Email
```bash
python test_onboarding.py
# Choose option 1 for student registration
# Enter your email
# Check inbox for welcome email
```

### Test Email Service Directly
```bash
python test_email_service.py
# Tests Resend configuration
# Sends test email to verify setup
```

### Manual API Testing
```bash
# 1. Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123","role":"student"}'

# 2. Check email for verification link

# 3. Verify (use token from email)
curl -X GET "http://localhost:8000/api/v1/auth/verify-email?token=YOUR_TOKEN"

# 4. Or test resend (use JWT from registration response)
curl -X POST http://localhost:8000/api/v1/auth/resend-verification \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Configuration

### Required Environment Variables
```bash
RESEND_API_KEY=re_28QHmQXc_4UyXTBGMbsvoRZjsgGUscgz4
RESEND_FROM_EMAIL=Base10 <noreply@cjalloh.com>
FRONTEND_URL=http://localhost:3000  # Update for production
```

### Database Schema
```sql
-- Users table columns for email verification
verification_token VARCHAR(255),           -- Secure token
verification_token_expires TIMESTAMP,      -- 24-hour expiry
verified_at TIMESTAMP,                     -- Verification timestamp
is_verified BOOLEAN DEFAULT FALSE,         -- Verification status
role VARCHAR(50) DEFAULT 'student',        -- User role
email VARCHAR(255) UNIQUE,                 -- User email
```

---

## Production Considerations

### Security
- ✅ Tokens are cryptographically secure (256-bit)
- ✅ Tokens expire after 24 hours
- ✅ Tokens are single-use (cleared after verification)
- ✅ Domain verified in Resend (cjalloh.com)
- ⚠️ Consider adding rate limiting to resend endpoint

### Performance
- ✅ Email sending is non-blocking (background tasks)
- ✅ No impact on registration response time
- ✅ Resend API is fast and reliable

### Monitoring
- Check logs for: `📧 Email sent successfully to {email}: {subject} (ID: {id})`
- Monitor Resend dashboard for delivery rates
- Track `verified_at` timestamps in database

### Scalability
- Consider using Celery for high-volume email sending
- Implement email queue with retry logic
- Add webhook handlers for Resend delivery events

---

## Support

**Documentation Files:**
- `EMAIL_ONBOARDING_GUIDE.md` - Complete integration guide
- `RESEND_INTEGRATION_SUMMARY.md` - Detailed summary
- `RESEND_QUICK_REFERENCE.md` - Quick reference card
- `EMAIL_FLOWS_DIAGRAM.md` - Visual flow diagrams

**Test Scripts:**
- `test_email_service.py` - Test Resend configuration
- `test_onboarding.py` - Test registration + email flow

**Resend Dashboard:** https://resend.com/emails
