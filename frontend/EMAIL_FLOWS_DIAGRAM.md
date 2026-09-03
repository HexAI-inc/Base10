# Base10 Email & Onboarding Flows

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Base10 Backend API                          │
│                                                                 │
│  ┌───────────────┐    ┌──────────────┐    ┌─────────────────┐ │
│  │  Auth Routes  │───▶│  Onboarding  │───▶│ Email Templates │ │
│  │  (register,   │    │   Service    │    │  (HTML/Text)    │ │
│  │   verify)     │    └──────┬───────┘    └─────────────────┘ │
│  └───────────────┘           │                                 │
│                               │                                 │
│                      ┌────────▼────────┐                        │
│                      │ Communication   │                        │
│                      │    Service      │                        │
│                      │  (_send_email)  │                        │
│                      └────────┬────────┘                        │
└─────────────────────────────┼──────────────────────────────────┘
                                │
                                ▼
                        ┌───────────────┐
                        │  Resend API   │
                        │ (resend.com)  │
                        └───────┬───────┘
                                │
                                ▼
                        ┌───────────────┐
                        │  User's Email │
                        │   Inbox 📧    │
                        └───────────────┘
```

## Student Registration Flow

```
┌─────────┐
│ Student │
│  Opens  │
│   App   │
└────┬────┘
     │
     │ 1. Fills registration form
     ▼
┌──────────────────┐
│ POST /register   │
│ {                │
│   email: "...",  │
│   password: "...",│
│   role: "student"│
│ }                │
└────┬─────────────┘
     │
     │ 2. User created in DB
     │    JWT token returned
     ▼
┌──────────────────────────┐
│ BackgroundTask started   │
│ OnboardingService        │
│   .send_welcome_email()  │
└────┬─────────────────────┘
     │
     │ 3. Generate verification token
     │    Store in user.verification_token
     ▼
┌────────────────────────────┐
│ Email Template Generated   │
│ - Welcome message          │
│ - Role-specific content    │
│ - Verification button      │
│ - Feature overview         │
└────┬───────────────────────┘
     │
     │ 4. Send via Resend API
     ▼
┌────────────────────────────┐
│ 📧 Welcome Email Delivered │
│                            │
│ Hi John,                   │
│ Welcome to Base10!         │
│                            │
│ ┌──────────────────────┐  │
│ │ Verify Your Email ▶  │  │
│ └──────────────────────┘  │
│                            │
│ Get Started:               │
│ 1. ✅ Verify email         │
│ 2. 📝 Complete profile     │
│ 3. 🎯 First quiz           │
└────┬───────────────────────┘
     │
     │ 5. Student clicks "Verify Email"
     ▼
┌────────────────────────────┐
│ GET /verify-email          │
│ ?token=abc123xyz           │
└────┬───────────────────────┘
     │
     │ 6. Token validated
     │    user.is_verified = True
     │    user.verified_at = now()
     ▼
┌────────────────────────────┐
│ ✅ Email Verified!         │
│                            │
│ Send post-verification     │
│ guidance email             │
└────┬───────────────────────┘
     │
     │ 7. Next steps guidance
     ▼
┌────────────────────────────┐
│ 📧 "Next Steps" Email      │
│                            │
│ Complete Your Profile:     │
│ - Add avatar               │
│ - Set learning prefs       │
│ - Choose study time        │
│                            │
│ Take Your First Quiz:      │
│ - Pick a subject           │
│ - Review AI explanations   │
│ - Track progress           │
└────────────────────────────┘
```

## Teacher Registration Flow

```
┌─────────┐
│ Teacher │
│  Joins  │
└────┬────┘
     │
     │ 1. POST /register (role: "teacher")
     ▼
┌────────────────────────────┐
│ 📧 Welcome Email           │
│                            │
│ Welcome to Your Teaching   │
│ Dashboard! 👨‍🏫             │
│                            │
│ Get Started:               │
│ 1. ✅ Verify email         │
│ 2. 🏫 Set up classroom     │
│ 3. 👥 Invite students      │
└────┬───────────────────────┘
     │
     │ 2. Verify email → GET /verify-email?token=xyz
     ▼
┌────────────────────────────┐
│ 📧 Post-Verification       │
│                            │
│ Create Your First Class:   │
│ - Name your classroom      │
│ - Get invite code          │
│ - Share with students      │
└────┬───────────────────────┘
     │
     │ 3. Teacher creates classroom
     │    POST /classrooms/create
     ▼
┌────────────────────────────┐
│ 📧 Classroom Created!      │
│                            │
│ Your classroom "SS3        │
│ Physics A" is ready!       │
│                            │
│ ╔════════════════════════╗ │
│ ║  CLASSROOM CODE        ║ │
│ ║                        ║ │
│ ║      ABC123            ║ │
│ ╚════════════════════════╝ │
│                            │
│ Students join:             │
│ 1. Open Base10             │
│ 2. Join Classroom          │
│ 3. Enter: ABC123           │
└────────────────────────────┘
```

## Parent Registration Flow

```
┌────────┐
│ Parent │
│  Joins │
└────┬───┘
     │
     │ 1. POST /register (role: "parent")
     ▼
┌────────────────────────────┐
│ 📧 Welcome Email           │
│                            │
│ Welcome! 👨‍👩‍👧             │
│                            │
│ Monitor your child's       │
│ progress!                  │
│                            │
│ Get Started:               │
│ 1. ✅ Verify email         │
│ 2. 👤 Complete profile     │
│ 3. 🔗 Link child account   │
└────┬───────────────────────┘
     │
     │ 2. Verify email
     ▼
┌────────────────────────────┐
│ 📧 Post-Verification       │
│                            │
│ Link to Your Child:        │
│ - Ask for their username   │
│ - Send linking request     │
│ - Wait for approval        │
│                            │
│ Set Preferences:           │
│ - Weekly/monthly reports   │
│ - SMS for milestones       │
│ - Study reminders          │
└────┬───────────────────────┘
     │
     │ 3. Every Sunday (automated)
     ▼
┌────────────────────────────┐
│ 📧 Weekly Summary          │
│                            │
│ Sarah's Progress This Week │
│                            │
│ ┌────────────────────────┐ │
│ │ 45 minutes study time  │ │
│ │ 23 questions answered  │ │
│ │ 87% overall accuracy   │ │
│ │ +5% from last week ↗   │ │
│ └────────────────────────┘ │
│                            │
│ 🌟 Strongest Subjects:     │
│ • Mathematics: 95%         │
│ • English: 90%             │
│                            │
│ ⚠️ Needs Attention:        │
│ • Physics: 65%             │
│ • Chemistry: 70%           │
└────────────────────────────┘
```

## Email Verification Token Flow

```
Registration
    │
    ├─▶ Generate token: secrets.token_urlsafe(32)
    │   Result: "XyZ123AbC456..."
    │
    ├─▶ Store in database:
    │   user.verification_token = "XyZ123AbC456..."
    │   user.verification_token_expires = now() + 24h
    │
    └─▶ Send in email:
        https://app.base10.app/verify-email?token=XyZ123AbC456...
        
        
User clicks link
    │
    ├─▶ Frontend receives token
    │   Calls: GET /api/v1/auth/verify-email?token=XyZ123AbC456...
    │
    ├─▶ Backend validates:
    │   • Find user with token
    │   • Check expiration (< 24h)
    │   • Token not already used
    │
    ├─▶ If valid:
    │   • user.is_verified = True
    │   • user.verified_at = now()
    │   • user.verification_token = None
    │   • user.verification_token_expires = None
    │
    └─▶ Send confirmation:
        • Return success response
        • Send post-verification email
        • Log verification event
```

## Weekly Report Automation Flow

```
┌──────────────────┐
│  Cron Job        │
│  (Every Sunday   │
│   at 9:00 AM)    │
└────┬─────────────┘
     │
     │ 1. Query all students
     │    with is_verified=True
     ▼
┌──────────────────────────────┐
│  For each student:           │
│  - Calculate weekly stats    │
│  - Questions answered        │
│  - Accuracy percentage       │
│  - Study minutes             │
│  - Top subjects              │
│  - Improvement areas         │
└────┬─────────────────────────┘
     │
     │ 2. Generate email template
     ▼
┌──────────────────────────────┐
│  get_weekly_report_email()   │
│  - User name                 │
│  - Stats object              │
│  - Dashboard URL             │
└────┬─────────────────────────┘
     │
     │ 3. Send via Resend
     ▼
┌──────────────────────────────┐
│  📧 Weekly Report Delivered  │
│                              │
│  📊 Your Weekly Report       │
│                              │
│  ┌────────────────────────┐  │
│  │ 42 Questions Answered  │  │
│  │ 85% Accuracy          │  │
│  │ 120 Study Minutes     │  │
│  └────────────────────────┘  │
│                              │
│  🏆 Top Subjects:            │
│  • English: 95%              │
│  • Mathematics: 90%          │
│                              │
│  📈 Areas for Improvement:   │
│  • Physics: 65%              │
│  • Chemistry: 70%            │
│                              │
│  ┌──────────────────────┐    │
│  │ View Full Dashboard  │    │
│  └──────────────────────┘    │
└──────────────────────────────┘
```

## Error Handling Flow

```
Email Send Attempt
    │
    ├─▶ Check API Key Valid?
    │   ├─ No ─▶ Log error ❌
    │   └─ Yes ─▶ Continue
    │
    ├─▶ Check User Email Exists?
    │   ├─ No ─▶ Skip email
    │   └─ Yes ─▶ Continue
    │
    ├─▶ Check User Verified?
    │   ├─ Already ─▶ Skip verification
    │   └─ No ─▶ Continue
    │
    ├─▶ Call Resend API
    │   │
    │   ├─ Success (200) ─▶ Log success ✅
    │   │                   Return email ID
    │   │
    │   ├─ Rate Limited (429) ─▶ Log warning
    │   │                        Retry later
    │   │
    │   ├─ Invalid From (400) ─▶ Log error
    │   │                        Check domain
    │   │
    │   └─ Server Error (5xx) ─▶ Log error
    │                            Alert ops
    │
    └─▶ Return success/failure
        to calling service
```

## Communication Priority Matrix

```
Priority Level │ Channels Used          │ Use Cases
───────────────┼────────────────────────┼─────────────────────────
CRITICAL       │ Push + SMS + Email     │ - Security alerts
               │ (All channels)         │ - Account compromised
               │                        │ - Payment failures
───────────────┼────────────────────────┼─────────────────────────
HIGH           │ Push + Email           │ - Password reset
               │ (or SMS if no app)     │ - Important updates
               │                        │ - Exam deadlines
───────────────┼────────────────────────┼─────────────────────────
MEDIUM         │ Email only             │ - Weekly reports
               │                        │ - Monthly summaries
               │                        │ - Feature announcements
───────────────┼────────────────────────┼─────────────────────────
LOW            │ Push only              │ - Study reminders
               │                        │ - Streak notifications
               │                        │ - Daily tips
```

## Database Schema

```
┌─────────────────────────────────────────────────────────────────┐
│                          users table                            │
├─────────────────────┬───────────────────────────────────────────┤
│ Column              │ Type                                      │
├─────────────────────┼───────────────────────────────────────────┤
│ id                  │ Integer (PK)                              │
│ email               │ String (unique, nullable)                 │
│ username            │ String (unique, nullable) [NEW]           │
│ phone_number        │ String (unique, nullable)                 │
│ hashed_password     │ String                                    │
│ full_name           │ String (nullable)                         │
│ role                │ String(50) [NEW]                          │
│ is_active           │ Boolean (default: True)                   │
│ is_verified         │ Boolean (default: False)                  │
│ verified_at         │ DateTime (nullable) [NEW]                 │
│ verification_token  │ String(255) (nullable) [NEW]              │
│ verification_token_ │ DateTime (nullable) [NEW]                 │
│ expires             │                                           │
│ created_at          │ DateTime                                  │
│ updated_at          │ DateTime                                  │
│ last_login          │ DateTime (nullable)                       │
└─────────────────────┴───────────────────────────────────────────┘
```

## File Structure

```
base10-backend/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── auth.py ─────────────┐ [Modified]
│   │           • register()          │ Added BackgroundTasks
│   │           • verify_email()      │ New endpoint
│   │           • resend_verification()│ New endpoint
│   │
│   ├── services/
│   │   ├── comms_service.py ────────┐ [Modified]
│   │   │   • _send_email()          │ Implemented with Resend
│   │   │
│   │   ├── onboarding_service.py ───┐ [NEW]
│   │   │   • send_welcome_email()   │ Main onboarding logic
│   │   │   • verify_email()         │ Token validation
│   │   │   • send_verification_reminder()
│   │   │   • send_classroom_created_email()
│   │   │
│   │   └── email_templates.py ──────┐ [NEW]
│   │       • get_welcome_email()    │ All HTML templates
│   │       • get_verification_email()
│   │       • get_password_reset_email()
│   │       • get_weekly_report_email()
│   │       • get_teacher_classroom_invite_email()
│   │       • get_parent_weekly_summary_email()
│   │
│   ├── models/
│   │   └── user.py ─────────────────┐ [Modified]
│   │       • verification_token      │ New fields
│   │       • verification_token_expires
│   │       • verified_at
│   │       • role
│   │       • username
│   │
│   └── core/
│       └── config.py ───────────────┐ [Modified]
│           • RESEND_API_KEY         │ New configs
│           • RESEND_FROM_EMAIL
│           • FRONTEND_URL
│
├── alembic/
│   └── versions/
│       └── add_email_verification_fields.py [NEW]
│
├── requirements.txt ────────────────┐ [Modified]
│   • resend==0.8.0                  │ Added Resend
│
├── .env.example ────────────────────┐ [Modified]
│   • RESEND_API_KEY                 │ New vars
│   • RESEND_FROM_EMAIL
│   • FRONTEND_URL
│
├── setup_email_service.sh ──────────┐ [NEW]
│   Automated setup script           │
│
├── EMAIL_ONBOARDING_GUIDE.md ───────┐ [NEW]
│   Complete documentation           │
│
├── RESEND_INTEGRATION_SUMMARY.md ───┐ [NEW]
│   Detailed summary                 │
│
└── RESEND_QUICK_REFERENCE.md ───────┐ [NEW]
    Quick reference card             │
```

---

**Legend:**
- 📧 = Email sent
- ✅ = Success/completion
- ❌ = Error/failure
- ▶ = Action button
- ↗ = Improvement/increase
- 🏆 = Achievement/top performer
- ⚠️ = Warning/attention needed
