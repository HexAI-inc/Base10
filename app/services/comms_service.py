"""
Notification Orchestrator - Unified Communication Layer.

Smart routing logic:
1. Push Notification (FREE) - If app installed
2. SMS (COSTS MONEY) - If no app, urgent alerts only
3. Email (ALWAYS) - Permanent records, reports

This saves costs by avoiding expensive SMS when free Push works.
"""
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from twilio.rest import Client
from app.core.config import settings

logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    """Message urgency levels."""
    LOW = "low"           # Can wait, use cheapest method
    MEDIUM = "medium"     # Important, prefer Push or Email
    HIGH = "high"         # Urgent, use SMS if needed
    CRITICAL = "critical" # Always use SMS + Push + Email


class MessageType(Enum):
    """Types of notifications."""
    STREAK_REMINDER = "streak_reminder"
    REVIEW_DUE = "review_due"
    PASSWORD_RESET = "password_reset"
    WEEKLY_REPORT = "weekly_report"
    MONTHLY_REPORT = "monthly_report"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    QUIZ_RESULT = "quiz_result"


class CommunicationService:
    """
    Smart router for user notifications.
    Decides the cheapest effective channel based on context.
    """
    
    def __init__(self):
        # Twilio SMS client (Phase 3)
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.twilio_client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
        else:
            self.twilio_client = None
            logger.warning("⚠️  Twilio not configured. SMS disabled.")
    
    
    def send_notification(
        self,
        user_id: int,
        message_type: MessageType,
        priority: MessagePriority,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        user_phone: Optional[str] = None,
        user_email: Optional[str] = None,
        has_app_installed: bool = False
    ) -> Dict[str, bool]:
        """
        Smart message routing.
        
        Args:
            user_id: User database ID
            message_type: Type of notification
            priority: How urgent is this message
            title: Notification title
            body: Notification content
            data: Optional JSON payload for push notifications
            user_phone: User's phone number (+220...)
            user_email: User's email
            has_app_installed: Whether user has mobile app
        
        Returns:
            Dict with delivery status per channel
        """
        results = {
            "push": False,
            "sms": False,
            "email": False
        }
        
        # RULE 1: Push Notification (FREE)
        if has_app_installed:
            results["push"] = self._send_push_notification(
                user_id, title, body, data
            )
            logger.info(f"📱 Push sent to user {user_id}")
        
        # RULE 2: SMS (COSTS MONEY - Only for urgent)
        # Only send SMS if:
        # - No app installed (can't receive push)
        # - Priority is HIGH or CRITICAL
        # - User has phone number
        should_send_sms = (
            not has_app_installed and
            priority in [MessagePriority.HIGH, MessagePriority.CRITICAL] and
            user_phone
        )
        
        if should_send_sms:
            results["sms"] = self._send_sms(user_phone, body)
            logger.info(f"📞 SMS sent to {user_phone}")
        
        # RULE 3: Email (ALWAYS for permanent records)
        # Send email for:
        # - Password resets (legal requirement)
        # - Reports (permanent record)
        # - Critical messages (backup channel)
        should_send_email = (
            user_email and (
                message_type in [
                    MessageType.PASSWORD_RESET,
                    MessageType.WEEKLY_REPORT,
                    MessageType.MONTHLY_REPORT
                ] or
                priority == MessagePriority.CRITICAL
            )
        )
        
        if should_send_email:
            # Check if message contains HTML formatting
            html_content = body if "<html>" in body or "<div" in body else None
            results["email"] = self._send_email(user_email, title, body, html=html_content)
            logger.info(f"📧 Email sent to {user_email}")
        
        return results
    
    
    def _send_push_notification(
        self,
        user_id: int,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send push notification via Firebase Cloud Messaging (FCM).
        
        Phase 2 implementation: Store device tokens in Redis.
        Mobile app registers token on login.
        """
        try:
            # TODO Phase 2: Integrate Firebase Admin SDK
            # from firebase_admin import messaging
            # 
            # token = redis_client.get(f"device_token:{user_id}")
            # message = messaging.Message(
            #     notification=messaging.Notification(title=title, body=body),
            #     data=data or {},
            #     token=token
            # )
            # messaging.send(message)
            
            logger.info(f"📱 Push notification queued: {title}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Push notification failed: {e}")
            return False
    
    
    def _send_sms(self, phone_number: str, message: str) -> bool:
        """
        Send SMS via Twilio (Phase 3).
        
        Cost optimization:
        - Only for urgent alerts
        - Max 160 chars (single SMS)
        - Batching for reports
        """
        if not self.twilio_client:
            logger.warning("⚠️  SMS disabled (Twilio not configured)")
            return False
        
        try:
            # Truncate to 160 chars to avoid multi-part SMS charges
            message = message[:160]
            
            sms = self.twilio_client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            
            logger.info(f"📞 SMS sent: {sms.sid}")
            return True
        
        except Exception as e:
            logger.error(f"❌ SMS failed: {e}")
            return False
    
    
    def _send_email(self, email: str, subject: str, body: str, html: str = None) -> bool:
        """
        Send email via Resend.

        Used for:
        - Password resets (legal requirement)
        - Monthly progress reports (PDF attachment)
        - Critical alerts (backup channel)
        - Welcome & onboarding emails
        - Weekly progress reports
        """
        try:
            import resend
            from app.core.config import settings

            # Check if API key is configured
            if not settings.RESEND_API_KEY:
                logger.warning("⚠️ RESEND_API_KEY not configured. Email sending disabled.")
                return False

            # Initialize Resend with API key
            resend.api_key = settings.RESEND_API_KEY

            # Send email
            params = {
                "from": settings.RESEND_FROM_EMAIL,
                "to": [email],
                "subject": subject,
            }

            # Use HTML if provided, otherwise plain text
            if html:
                params["html"] = html
            else:
                params["text"] = body

            response = resend.Emails.send(params)

            logger.info(f"📧 Email sent successfully to {email}: {subject} (ID: {response.get('id', 'unknown')})")
            return True

        except Exception as e:
            logger.error(f"❌ Email failed to {email}: {e}")
            return False


# Celery task for async sending (Phase 2)
# @celery_app.task
# def send_notification_async(user_id, message_type, priority, title, body, **kwargs):
#     """Background task to avoid blocking API responses."""
#     service = CommunicationService()
#     service.send_notification(user_id, message_type, priority, title, body, **kwargs)


# Example usage:
if __name__ == "__main__":
    service = CommunicationService()
    
    # Example 1: Daily streak reminder (LOW priority, app user)
    service.send_notification(
        user_id=123,
        message_type=MessageType.STREAK_REMINDER,
        priority=MessagePriority.LOW,
        title="Keep your streak! 🔥",
        body="You haven't practiced today. 5 minutes to maintain your 7-day streak!",
        has_app_installed=True
    )
    # Result: Push only (FREE)
    
    # Example 2: Password reset (CRITICAL, no app)
    service.send_notification(
        user_id=456,
        message_type=MessageType.PASSWORD_RESET,
        priority=MessagePriority.CRITICAL,
        title="Reset your password",
        body="Click here to reset: https://base10.edu/reset/abc123",
        user_phone="+2207777777",
        user_email="student@example.com",
        has_app_installed=False
    )
    # Result: SMS + Email (urgent, no app to receive push)
    
    # Example 3: Monthly report (MEDIUM, has app)
    service.send_notification(
        user_id=789,
        message_type=MessageType.MONTHLY_REPORT,
        priority=MessagePriority.MEDIUM,
        title="Your December progress 📊",
        body="You answered 250 questions this month! 78% accuracy. View report.",
        user_email="student@example.com",
        has_app_installed=True
    )
    # Result: Push + Email (permanent record)
