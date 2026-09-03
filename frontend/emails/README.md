# Base10 Email Templates

All email templates follow Base10's design language with emerald-purple gradients, modern typography, and mobile-responsive layouts.

## Template Variables

Replace these placeholders with actual values before sending:

### Welcome Emails
- `{{userName}}` - User's first name or full name
- `{{verificationUrl}}` - Full URL with verification token

### Verification Reminder
- `{{userName}}` - User's name
- `{{verificationUrl}}` - Full URL with verification token

### Weekly Report
- `{{userName}}` - User's name
- `{{questionsAnswered}}` - Number of questions (e.g., "42")
- `{{accuracy}}` - Overall accuracy percentage (e.g., "85")
- `{{studyMinutes}}` - Minutes studied (e.g., "120")
- `{{topSubject1Name}}` - Name of best subject
- `{{topSubject1Accuracy}}` - Accuracy for best subject
- `{{topSubject2Name}}` - Name of 2nd best subject
- `{{topSubject2Accuracy}}` - Accuracy for 2nd best subject
- `{{weakSubject1Name}}` - Name of weakest subject
- `{{weakSubject1Accuracy}}` - Accuracy for weakest subject
- `{{weakSubject2Name}}` - Name of 2nd weakest subject
- `{{weakSubject2Accuracy}}` - Accuracy for 2nd weakest subject
- `{{dashboardUrl}}` - Full URL to dashboard
- `{{unsubscribeUrl}}` - Unsubscribe link

## Files

1. **welcome-student.html** - Welcome email for students
2. **welcome-teacher.html** - Welcome email for teachers
3. **welcome-parent.html** - Welcome email for parents
4. **verification-reminder.html** - Resend verification email
5. **weekly-report.html** - Weekly progress report

## Design Features

- **Colors**: Emerald-500 (#10b981) + Purple-500 (#8b5cf6) gradient
- **Typography**: System font stack, 800 weight headings
- **Mobile-Responsive**: Max-width 600px, works on all email clients
- **Accessibility**: WCAG AA compliant color contrasts
- **Brand Consistency**: Matches web app design language

## Testing

Test emails in:
- Gmail (web + mobile)
- Outlook (desktop + web)
- Apple Mail (macOS + iOS)
- Samsung Email (Android)

## Usage with Backend

Send these templates via Resend API:

```python
# Example Python backend code
from resend import Resend

resend = Resend(api_key="your_key")

# Read template
with open('emails/welcome-student.html', 'r') as f:
    html_template = f.read()

# Replace variables
html_content = html_template.replace('{{userName}}', 'John')
html_content = html_content.replace('{{verificationUrl}}', verification_url)

# Send
resend.emails.send({
    "from": "Base10 <noreply@cjalloh.com>",
    "to": "student@example.com",
    "subject": "Welcome to Base10 - Verify Your Email",
    "html": html_content
})
```

## Plain Text Fallback

For email clients that don't support HTML, provide plain text version:

```
Base10 - Master Your WAEC Exams

Hi John,

Welcome to Your Learning Journey!

Verify your email: [verification_url]

Get Started:
1. Verify your email address
2. Complete your profile
3. Take your first quiz

---
Base10 | support@base10.app
© 2025 Base10. All rights reserved.
```
