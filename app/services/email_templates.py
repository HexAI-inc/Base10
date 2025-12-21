"""
Email Templates with HTML formatting for Resend
Uses templates from app/emails/ folder
"""
from typing import Dict, Any
import os


def _read_email_template(filename: str) -> str:
    """Read email template from app/emails/ directory"""
    template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'emails', filename)
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def get_welcome_email(user_name: str, user_role: str, verification_url: str) -> Dict[str, str]:
    """
    Role-based welcome email template
    Uses HTML templates from app/emails/ folder
    """
    # Map role to template file
    template_map = {
        "STUDENT": "welcome-student.html",
        "TEACHER": "welcome-teacher.html",
        "PARENT": "welcome-parent.html"
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


def get_verification_email(user_name: str, verification_url: str) -> Dict[str, str]:
    """
    Email verification reminder
    Uses verification-reminder.html template
    """
    html_content = _read_email_template("verification-reminder.html")
    
    # Replace template variables
    html_content = html_content.replace("{{userName}}", user_name)
    html_content = html_content.replace("{{verificationUrl}}", verification_url)
    
    return {
        "subject": "Verify Your Base10 Email Address",
        "html": html_content
    }


def get_weekly_report_email(user_name: str, stats: Dict[str, Any]) -> Dict[str, str]:
    """
    Weekly progress report for students
    Uses weekly-report.html template
    """
    html_content = _read_email_template("weekly-report.html")
    
    # Replace template variables
    html_content = html_content.replace("{{userName}}", user_name)
    html_content = html_content.replace("{{questionsAnswered}}", str(stats.get('questions_answered', 0)))
    html_content = html_content.replace("{{accuracy}}", str(stats.get('accuracy', 0)))
    html_content = html_content.replace("{{studyMinutes}}", str(stats.get('study_minutes', 0)))
    
    # Top subjects (default to placeholders if not provided)
    top_subjects = stats.get('top_subjects', [])
    html_content = html_content.replace("{{topSubject1Name}}", top_subjects[0]['name'] if len(top_subjects) > 0 else "Mathematics")
    html_content = html_content.replace("{{topSubject1Accuracy}}", str(top_subjects[0]['accuracy']) if len(top_subjects) > 0 else "0")
    html_content = html_content.replace("{{topSubject2Name}}", top_subjects[1]['name'] if len(top_subjects) > 1 else "English")
    html_content = html_content.replace("{{topSubject2Accuracy}}", str(top_subjects[1]['accuracy']) if len(top_subjects) > 1 else "0")
    
    # Weak subjects (default to placeholders if not provided)
    weak_subjects = stats.get('improvement_areas', [])
    html_content = html_content.replace("{{weakSubject1Name}}", weak_subjects[0]['name'] if len(weak_subjects) > 0 else "Physics")
    html_content = html_content.replace("{{weakSubject1Accuracy}}", str(weak_subjects[0]['accuracy']) if len(weak_subjects) > 0 else "0")
    html_content = html_content.replace("{{weakSubject2Name}}", weak_subjects[1]['name'] if len(weak_subjects) > 1 else "Chemistry")
    html_content = html_content.replace("{{weakSubject2Accuracy}}", str(weak_subjects[1]['accuracy']) if len(weak_subjects) > 1 else "0")
    
    # Dashboard and unsubscribe URLs
    html_content = html_content.replace("{{dashboardUrl}}", stats.get('dashboard_url', '#'))
    html_content = html_content.replace("{{unsubscribeUrl}}", stats.get('unsubscribe_url', '#'))
    
    return {
        "subject": f"Your Weekly Progress Report 📊",
        "html": html_content
    }


# Note: password_reset, classroom_invite, and parent_summary emails use inline templates
# These will be moved to HTML files in future updates

def get_password_reset_email(user_name: str, reset_url: str) -> Dict[str, str]:
    """
    Password reset email (inline template - TODO: move to HTML file)
    """
    return {
        "subject": "Reset Your Base10 Password",
        "html": f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: #667eea; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
        <h2 style="color: white; margin: 0;">🔒 Password Reset Request</h2>
    </div>
    
    <div style="background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; border-top: none;">
        <p>Hi {user_name},</p>
        <p>We received a request to reset your Base10 password. Click the button below to create a new password:</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_url}" 
               style="background: #667eea; color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                Reset Password
            </a>
        </div>
        
        <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0;">
            <p style="margin: 0; color: #856404;">
                <strong>⚠️ Security Notice:</strong> If you didn't request this password reset, please ignore this email. Your password will remain unchanged.
            </p>
        </div>
        
        <p style="font-size: 14px; color: #666; margin-top: 30px;">
            If the button doesn't work, copy and paste this link:<br>
            <a href="{reset_url}" style="color: #667eea; word-break: break-all;">{reset_url}</a>
        </p>
        
        <p style="font-size: 12px; color: #999; margin-top: 30px;">
            This link expires in 1 hour for security reasons.
        </p>
    </div>
</body>
</html>
        """
    }


def get_teacher_classroom_invite_email(teacher_name: str, classroom_name: str, invite_code: str) -> Dict[str, str]:
    """
    Teacher classroom creation confirmation (inline template - TODO: move to HTML file)
    """
    return {
        "subject": f"Your Classroom '{classroom_name}' is Ready!",
        "html": f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: #667eea; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
        <h2 style="color: white; margin: 0;">🏫 Classroom Created!</h2>
    </div>
    
    <div style="background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; border-top: none;">
        <p>Hi {teacher_name},</p>
        <p>Your classroom <strong>"{classroom_name}"</strong> is ready! Share this invite code with your students:</p>
        
        <div style="background: #f8f9fa; border: 2px dashed #667eea; padding: 30px; text-align: center; margin: 30px 0; border-radius: 8px;">
            <div style="font-size: 14px; color: #666; margin-bottom: 10px;">CLASSROOM CODE</div>
            <div style="font-size: 36px; font-weight: bold; color: #667eea; letter-spacing: 4px; font-family: monospace;">{invite_code}</div>
        </div>
        
        <h3 style="color: #667eea;">How Students Join:</h3>
        <ol style="padding-left: 20px;">
            <li>Open Base10 app</li>
            <li>Go to "Join Classroom"</li>
            <li>Enter code: <code style="background: #f8f9fa; padding: 2px 6px; border-radius: 3px;">{invite_code}</code></li>
        </ol>
        
        <div style="background: #d1ecf1; border-left: 4px solid #17a2b8; padding: 15px; margin: 20px 0;">
            <p style="margin: 0; color: #0c5460;">
                <strong>💡 Pro Tip:</strong> You can also share this code via WhatsApp, text message, or write it on the board!
            </p>
        </div>
    </div>
</body>
</html>
        """
    }


def _format_subject_list(subjects: list) -> str:
    """Helper to format subject performance lists"""
    if not subjects:
        return "<p style='margin: 0; color: #666;'>No data available yet. Keep practicing!</p>"
    
    html = "<ul style='margin: 10px 0; padding-left: 20px;'>"
    for subject in subjects:
        html += f"<li style='margin: 5px 0;'><strong>{subject.get('name', '')}</strong>: {subject.get('accuracy', 0)}% accuracy</li>"
    html += "</ul>"
    return html


def get_parent_weekly_summary_email(parent_name: str, student_name: str, stats: Dict[str, Any]) -> Dict[str, str]:
    """
    Weekly summary for parents (inline template - TODO: move to HTML file)
    """
    return {
        "subject": f"{student_name}'s Weekly Learning Summary",
        "html": f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
        <h2 style="color: white; margin: 0;">👨‍👩‍👧 Parent Report</h2>
        <p style="color: #f0f0f0; margin: 10px 0 0 0;">{student_name}'s Progress</p>
    </div>
    
    <div style="background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; border-top: none;">
        <p style="font-size: 16px;">Hi {parent_name},</p>
        <p>Here's how {student_name} performed this week:</p>
        
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <div style="margin-bottom: 15px;">
                <strong style="color: #667eea;">Study Time:</strong> {stats.get('study_minutes', 0)} minutes
            </div>
            <div style="margin-bottom: 15px;">
                <strong style="color: #667eea;">Questions Attempted:</strong> {stats.get('questions_answered', 0)}
            </div>
            <div style="margin-bottom: 15px;">
                <strong style="color: #667eea;">Overall Accuracy:</strong> {stats.get('accuracy', 0)}%
            </div>
            <div>
                <strong style="color: #667eea;">Improvement:</strong> 
                <span style="color: {'#28a745' if stats.get('accuracy_change', 0) > 0 else '#dc3545'};">
                    {'+' if stats.get('accuracy_change', 0) > 0 else ''}{stats.get('accuracy_change', 0)}% from last week
                </span>
            </div>
        </div>
        
        <h3 style="color: #667eea;">Strongest Subjects 🌟</h3>
        <div style="background: #d4edda; padding: 15px; border-radius: 5px; border-left: 4px solid #28a745;">
            {_format_subject_list(stats.get('top_subjects', []))}
        </div>
        
        <h3 style="color: #667eea; margin-top: 20px;">Needs Attention ⚠️</h3>
        <div style="background: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107;">
            {_format_subject_list(stats.get('improvement_areas', []))}
        </div>
        
        <div style="background: #d1ecf1; border-left: 4px solid #17a2b8; padding: 15px; margin: 30px 0;">
            <p style="margin: 0; color: #0c5460;">
                <strong>💡 Recommendation:</strong> {stats.get('recommendation', 'Encourage consistent daily practice for best results.')}
            </p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{stats.get('dashboard_url', '#')}" 
               style="background: #667eea; color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                View Detailed Progress
            </a>
        </div>
    </div>
    
    <div style="background: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; font-size: 12px; color: #999;">
        <p style="margin: 5px 0;">© 2025 Base10. All rights reserved.</p>
    </div>
</body>
</html>
        """
    }

