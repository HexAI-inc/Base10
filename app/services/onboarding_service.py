"""
User Onboarding Service
Handles welcome emails, verification flows, and role-based onboarding sequences
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.email_templates import (
    get_welcome_email,
    get_verification_email,
    get_teacher_classroom_invite_email
)
from app.services.comms_service import CommunicationService, MessageType, MessagePriority
from app.core.config import settings
import secrets
import logging

logger = logging.getLogger(__name__)


class OnboardingService:
    """
    Manages user onboarding flows for different user types
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.comms_service = CommunicationService()
    
    async def send_welcome_email(self, user: User) -> bool:
        """
        Send role-specific welcome email with verification link
        """
        try:
            # Generate verification token
            verification_token = self._generate_verification_token(user)
            
            # Build verification URL
            verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
            
            # Get role-specific welcome email
            email_data = get_welcome_email(
                user_name=user.full_name or user.username,
                user_role=user.role,
                verification_url=verification_url
            )
            
            # Send via communication service
            success = self.comms_service._send_email(
                email=user.email,
                subject=email_data["subject"],
                body="",  # Not used when HTML is provided
                html=email_data["html"]
            )
            
            if success:
                logger.info(f"✅ Welcome email sent to {user.email} (role: {user.role})")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to send welcome email to {user.email}: {e}")
            return False
    
    async def send_verification_reminder(self, user: User) -> bool:
        """
        Send verification reminder to unverified users
        """
        try:
            if user.is_verified:
                logger.info(f"User {user.email} already verified, skipping reminder")
                return False
            
            # Generate new verification token
            verification_token = self._generate_verification_token(user)
            verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
            
            # Get verification email
            email_data = get_verification_email(
                user_name=user.full_name or user.username,
                verification_url=verification_url
            )
            
            # Send email
            success = self.comms_service._send_email(
                email=user.email,
                subject=email_data["subject"],
                body="",
                html=email_data["html"]
            )
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to send verification reminder to {user.email}: {e}")
            return False
    
    async def verify_email(self, token: str) -> Optional[User]:
        """
        Verify user email with token
        """
        try:
            # Find user by verification token
            user = self.db.query(User).filter(
                User.verification_token == token
            ).first()
            
            if not user:
                logger.warning(f"Invalid verification token: {token}")
                return None
            
            # Check token expiration (24 hours)
            if user.verification_token_expires and user.verification_token_expires < datetime.utcnow():
                logger.warning(f"Expired verification token for user {user.email}")
                return None
            
            # Mark as verified
            user.is_verified = True
            user.verification_token = None
            user.verification_token_expires = None
            user.verified_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"✅ Email verified for user {user.email}")
            
            # Send post-verification onboarding email based on role
            await self._send_post_verification_guidance(user)
            
            return user
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Email verification failed: {e}")
            return None
    
    async def _send_post_verification_guidance(self, user: User):
        """
        Send role-specific guidance after email verification
        """
        try:
            guidance = self._get_onboarding_guidance(user.role)
            
            # Send simple text email with next steps
            self.comms_service._send_email(
                email=user.email,
                subject=f"Next Steps: Complete Your {user.role.title()} Profile",
                body=guidance,
                html=self._format_guidance_html(user, guidance)
            )
            
        except Exception as e:
            logger.error(f"Failed to send post-verification guidance: {e}")
    
    def _get_onboarding_guidance(self, role: str) -> str:
        """
        Get role-specific onboarding guidance
        """
        guidance = {
            "student": """
Welcome to Base10! 🎓

Now that your email is verified, here's what to do next:

1. Complete Your Profile
   - Add your avatar
   - Set your learning preferences
   - Choose your study time

2. Take Your First Practice Quiz
   - Start with your strongest subject
   - Review the AI-powered explanations
   - Track your progress on the dashboard

3. Join a Classroom (Optional)
   - Ask your teacher for a classroom code
   - Get access to class leaderboards
   - Receive teacher-assigned practice

Let's get started! 🚀
            """,
            "teacher": """
Welcome to Base10! 👨‍🏫

Now that your email is verified, here's what to do next:

1. Create Your First Classroom
   - Give it a name (e.g., "SS3 Physics Class A")
   - Get your unique classroom code
   - Share the code with your students

2. Invite Your Students
   - Students join using the classroom code
   - Monitor their practice activity
   - View performance analytics

3. Use Analytics to Guide Teaching
   - Identify struggling students
   - See which topics need review
   - Assign targeted practice materials

Let's empower your students! 💡
            """,
            "parent": """
Welcome to Base10! 👨‍👩‍👧

Now that your email is verified, here's what to do next:

1. Link to Your Child's Account
   - Ask your child for their username
   - Send a linking request
   - Wait for approval

2. Set Up Your Preferences
   - Choose report frequency (weekly/monthly)
   - Enable SMS notifications for milestones
   - Set study reminder preferences

3. Monitor Progress
   - View weekly progress reports
   - Celebrate achievements together
   - Encourage consistent practice

Let's support their learning journey! 📚
            """
        }
        
        return guidance.get(role, guidance["student"])
    
    def _format_guidance_html(self, user: User, guidance: str) -> str:
        """
        Format guidance as HTML email
        """
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: #667eea; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
        <h2 style="color: white; margin: 0;">✅ Email Verified!</h2>
    </div>
    
    <div style="background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; border-top: none;">
        <p>Hi {user.full_name or user.username},</p>
        <pre style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; white-space: pre-wrap; line-height: 1.8;">{guidance}</pre>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{settings.FRONTEND_URL}/dashboard" 
               style="background: #667eea; color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                Go to Dashboard
            </a>
        </div>
    </div>
</body>
</html>
        """
    
    def _generate_verification_token(self, user: User) -> str:
        """
        Generate and store verification token for user
        """
        # Generate secure random token
        token = secrets.token_urlsafe(32)
        
        # Store in database with expiration
        user.verification_token = token
        user.verification_token_expires = datetime.utcnow() + timedelta(hours=24)
        
        self.db.commit()
        
        return token
    
    async def send_classroom_created_email(self, teacher: User, classroom_name: str, invite_code: str) -> bool:
        """
        Send confirmation email when teacher creates a classroom
        """
        try:
            email_data = get_teacher_classroom_invite_email(
                teacher_name=teacher.full_name or teacher.username,
                classroom_name=classroom_name,
                invite_code=invite_code
            )
            
            success = self.comms_service._send_email(
                email=teacher.email,
                subject=email_data["subject"],
                body="",
                html=email_data["html"]
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send classroom creation email: {e}")
            return False
