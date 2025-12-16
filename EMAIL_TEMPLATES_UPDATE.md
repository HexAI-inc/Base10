# Email Templates Update

## Overview
Updated email service to use dedicated HTML template files from the `app/emails/` folder instead of inline Python strings.

## Changes Made

### New HTML Template Files
Created 5 professional email templates in `app/emails/`:

1. **welcome-student.html** - Student onboarding with practice quiz focus
2. **welcome-teacher.html** - Teacher dashboard intro with classroom management
3. **welcome-parent.html** - Parent monitoring features and weekly reports
4. **verification-reminder.html** - Simple email verification request
5. **weekly-report.html** - Student progress report with stats and subjects

### Design Features
- **Modern UI**: Green (#10b981) and purple (#8b5cf6) gradient branding
- **Mobile-Responsive**: Proper viewport and inline CSS for email clients
- **Consistent Layout**: Header with Base10 logo, content area, footer
- **Role-Specific**: Different welcome emails for students, teachers, and parents
- **Clear CTAs**: Prominent verification buttons with fallback text links

### Template Variables
All templates use `{{variableName}}` syntax for dynamic content:

```python
# Example: Welcome Email
{{userName}}           # User's name
{{verificationUrl}}    # Verification link

# Example: Weekly Report
{{questionsAnswered}}  # Number of questions
{{accuracy}}           # Percentage accuracy
{{studyMinutes}}       # Study time
{{topSubject1Name}}    # Best subject name
{{topSubject1Accuracy}}# Best subject accuracy
{{weakSubject1Name}}   # Needs improvement
{{weakSubject1Accuracy}}
{{dashboardUrl}}       # Link to dashboard
{{unsubscribeUrl}}     # Unsubscribe link
```

### Refactored Code
Updated `app/services/email_templates.py`:

```python
def _read_email_template(filename: str) -> str:
    """Read email template from app/emails/ directory"""
    template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'emails', filename)
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def get_welcome_email(user_name: str, user_role: str, verification_url: str) -> Dict[str, str]:
    """Role-based welcome email using HTML templates"""
    template_map = {
        "student": "welcome-student.html",
        "teacher": "welcome-teacher.html",
        "parent": "welcome-parent.html"
    }
    
    template_file = template_map.get(user_role.lower(), "welcome-student.html")
    html_content = _read_email_template(template_file)
    
    # Replace template variables
    html_content = html_content.replace("{{userName}}", user_name)
    html_content = html_content.replace("{{verificationUrl}}", verification_url)
    
    return {
        "subject": f"Welcome to Base10, {user_name}! 🎉",
        "html": html_content
    }
```

### Backward Compatibility
The following emails still use inline templates (to be migrated later):
- `get_password_reset_email()` - Password reset flow
- `get_teacher_classroom_invite_email()` - Classroom creation
- `get_parent_weekly_summary_email()` - Parent reports

## Testing
All templates tested successfully:
```bash
✅ Welcome email (student) loaded successfully
✅ Welcome email (teacher) loaded successfully  
✅ Welcome email (parent) loaded successfully
✅ Verification email loaded successfully
✅ Weekly report email loaded successfully
✅ All template variables replaced correctly
```

## Benefits

### 1. Easier Maintenance
- Edit HTML files directly without touching Python code
- No more escaping quotes or managing multi-line strings
- Better syntax highlighting in HTML editors

### 2. Designer-Friendly
- Non-developers can update email designs
- Version control for email templates
- A/B test different designs easily

### 3. Consistency
- All emails share the same header/footer structure
- Unified color scheme and branding
- Consistent mobile responsiveness

### 4. Professional Quality
- Clean, modern design matching Base10 brand
- Mobile-optimized for all email clients
- Clear call-to-action buttons with proper styling

## Next Steps

### Immediate (Optional)
1. Add password reset HTML template
2. Add classroom invite HTML template  
3. Add parent weekly summary HTML template

### Future Enhancements
1. Use a template engine like Jinja2 for advanced logic
2. Add email preview endpoint for testing
3. Create email template builder UI for admins
4. A/B testing framework for email effectiveness

## Files Changed
- `app/emails/welcome-student.html` (NEW)
- `app/emails/welcome-teacher.html` (NEW)
- `app/emails/welcome-parent.html` (NEW)
- `app/emails/verification-reminder.html` (NEW)
- `app/emails/weekly-report.html` (NEW)
- `app/emails/README.md` (NEW)
- `app/services/email_templates.py` (MODIFIED)

## Git Commit
```
refactor: Update email templates to use HTML files from app/emails

- Add 5 HTML email templates
- Refactor email_templates.py to read from HTML files
- Use template variable replacement ({{userName}}, etc.)
- Maintain backward compatibility for inline templates
- Templates use Base10 branding (green/purple gradients)
- Mobile-responsive design for all email clients

Commit: d47620b
```

## Usage Example
```python
from app.services.onboarding_service import OnboardingService

# Send welcome email (automatically uses correct template based on role)
onboarding = OnboardingService(db)
await onboarding.send_welcome_email(user)  # user.role = "student"/"teacher"/"parent"

# Send weekly report
from app.services.comms_service import CommunicationService
comms = CommunicationService()

stats = {
    'questions_answered': 150,
    'accuracy': 85,
    'study_minutes': 240,
    'top_subjects': [
        {'name': 'Mathematics', 'accuracy': 92},
        {'name': 'English', 'accuracy': 88}
    ],
    'improvement_areas': [
        {'name': 'Physics', 'accuracy': 65},
        {'name': 'Chemistry', 'accuracy': 70}
    ],
    'dashboard_url': 'https://base10.app/dashboard',
    'unsubscribe_url': 'https://base10.app/unsubscribe'
}

comms.send_weekly_report(user.email, user.name, stats)
```

---
**Status**: ✅ Deployed to production (commit d47620b)
**Date**: December 16, 2025
