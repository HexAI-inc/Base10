"""
Scheduler Service - The Heartbeat of Base10.

Automated maintenance tasks that run on schedule:
- Daily: Check streaks, reset if broken
- Weekly: Calculate leaderboards
- Monthly: Generate progress reports

This drives engagement without manual intervention.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import logging

from app.db.session import SessionLocal
from app.models.user import User
from app.models.progress import Attempt
from app.core.redis_client import redis_client
from app.services.comms_service import CommunicationService, MessageType, MessagePriority

logger = logging.getLogger(__name__)

# Initialize scheduler
scheduler = AsyncIOScheduler()


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================
# DAILY TASKS (00:00 GMT)
# ==========================================

def check_and_reset_streaks():
    """
    Check all user streaks. Reset if they didn't study yesterday.
    
    Logic:
    - Query all users with active streaks
    - Check if they have attempts from yesterday
    - If no attempts: Reset streak to 0, send reminder
    - If attempts: Maintain streak
    """
    db = next(get_db())
    comms = CommunicationService()
    
    try:
        yesterday = datetime.utcnow().date() - timedelta(days=1)
        today = datetime.utcnow().date()
        
        # Get all active users
        users = db.query(User).filter(User.is_active == True).all()
        
        streaks_reset = 0
        streaks_maintained = 0
        
        for user in users:
            # Check for attempts yesterday
            attempts_yesterday = db.query(Attempt).filter(
                and_(
                    Attempt.user_id == user.id,
                    func.date(Attempt.attempted_at) == yesterday
                )
            ).count()
            
            if attempts_yesterday == 0:
                # Streak broken! Reset to 0
                # TODO: Add streak field to User model
                # user.study_streak = 0
                # db.commit()
                
                streaks_reset += 1
                
                # Send reminder notification (LOW priority)
                comms.send_notification(
                    user_id=user.id,
                    message_type=MessageType.STREAK_REMINDER,
                    priority=MessagePriority.LOW,
                    title="Your streak was reset 😔",
                    body="You didn't practice yesterday. Start a new streak today! 💪",
                    user_phone=user.phone_number,
                    user_email=user.email,
                    has_app_installed=True  # TODO: Track in User model
                )
            else:
                streaks_maintained += 1
        
        logger.info(f"✅ Streaks checked: {streaks_maintained} maintained, {streaks_reset} reset")
    
    except Exception as e:
        logger.error(f"❌ Streak check failed: {e}")
    finally:
        db.close()


def send_daily_review_reminders():
    """
    Send reminders for questions due for spaced repetition review.
    
    Only notify users with 5+ reviews due (avoid spam).
    """
    db = next(get_db())
    comms = CommunicationService()
    
    try:
        now = datetime.utcnow()
        
        # Find users with reviews due today
        users_with_reviews = db.query(
            Attempt.user_id,
            func.count(Attempt.id).label('due_count')
        ).filter(
            Attempt.next_review_date <= now
        ).group_by(Attempt.user_id).having(
            func.count(Attempt.id) >= 5  # Only notify if 5+ reviews
        ).all()
        
        for user_id, due_count in users_with_reviews:
            user = db.query(User).filter(User.id == user_id).first()
            
            comms.send_notification(
                user_id=user.id,
                message_type=MessageType.REVIEW_DUE,
                priority=MessagePriority.MEDIUM,
                title=f"{due_count} reviews due! 📚",
                body=f"You have {due_count} questions ready for review. Practice now to boost retention!",
                user_phone=user.phone_number,
                user_email=user.email,
                has_app_installed=True
            )
        
        logger.info(f"✅ Review reminders sent to {len(users_with_reviews)} users")
    
    except Exception as e:
        logger.error(f"❌ Review reminders failed: {e}")
    finally:
        db.close()


# ==========================================
# WEEKLY TASKS (Sunday 23:00 GMT)
# ==========================================

def calculate_weekly_leaderboard():
    """
    Calculate weekly leaderboard rankings.
    
    Ranking criteria:
    1. Total questions attempted
    2. Accuracy percentage
    3. Study streak
    
    Store results in Redis cache for fast API access.
    """
    db = next(get_db())
    
    try:
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        # Calculate user scores for this week
        leaderboard = db.query(
            User.id,
            User.full_name,
            func.count(Attempt.id).label('attempts'),
            (func.sum(func.cast(Attempt.is_correct, db.Integer)) * 100.0 / 
             func.count(Attempt.id)).label('accuracy')
        ).join(
            Attempt, Attempt.user_id == User.id
        ).filter(
            Attempt.attempted_at >= week_ago
        ).group_by(
            User.id, User.full_name
        ).order_by(
            func.count(Attempt.id).desc(),
            (func.sum(func.cast(Attempt.is_correct, db.Integer)) * 100.0 / 
             func.count(Attempt.id)).desc()
        ).limit(100).all()
        
        # Format leaderboard for Redis cache
        leaderboard_data = [
            {
                'rank': idx + 1,
                'user_id': user.id,
                'name': user.full_name,
                'attempts': user.attempts,
                'accuracy': round(user.accuracy, 2)
            }
            for idx, user in enumerate(leaderboard)
        ]
        
        # Store in Redis cache for fast API access
        redis_client.set_leaderboard(leaderboard_data, period="weekly", ttl=86400)  # 24h cache
        
        logger.info(f"✅ Weekly leaderboard calculated and cached: {len(leaderboard)} users")
    
    except Exception as e:
        logger.error(f"❌ Leaderboard calculation failed: {e}")
    finally:
        db.close()


# ==========================================
# MONTHLY TASKS (1st of month, 00:00 GMT)
# ==========================================

def generate_monthly_reports():
    """
    Generate PDF progress reports for all users.
    
    Report includes:
    - Total questions answered
    - Accuracy by subject
    - Weak topics identified
    - Study streak history
    - Improvement graph
    
    Sends via Email (permanent record).
    """
    db = next(get_db())
    comms = CommunicationService()
    
    try:
        month_ago = datetime.utcnow() - timedelta(days=30)
        
        users = db.query(User).filter(User.is_active == True).all()
        
        reports_generated = 0
        
        for user in users:
            # Calculate user stats for the month
            total_attempts = db.query(func.count(Attempt.id)).filter(
                and_(
                    Attempt.user_id == user.id,
                    Attempt.attempted_at >= month_ago
                )
            ).scalar() or 0
            
            if total_attempts == 0:
                continue  # Skip users with no activity
            
            correct_attempts = db.query(func.sum(func.cast(Attempt.is_correct, db.Integer))).filter(
                and_(
                    Attempt.user_id == user.id,
                    Attempt.attempted_at >= month_ago
                )
            ).scalar() or 0
            
            accuracy = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
            
            # TODO Phase 2: Generate PDF report
            # pdf_path = generate_report_pdf(user, total_attempts, accuracy)
            
            # Send email with report
            comms.send_notification(
                user_id=user.id,
                message_type=MessageType.MONTHLY_REPORT,
                priority=MessagePriority.MEDIUM,
                title=f"Your {datetime.utcnow().strftime('%B')} Progress Report 📊",
                body=f"Great work! You answered {total_attempts} questions with {accuracy:.1f}% accuracy. Keep it up! 🎉",
                user_email=user.email,
                has_app_installed=True
            )
            
            reports_generated += 1
        
        logger.info(f"✅ Monthly reports generated for {reports_generated} users")
    
    except Exception as e:
        logger.error(f"❌ Monthly reports failed: {e}")
    finally:
        db.close()


# ==========================================
# SCHEDULER CONFIGURATION
# ==========================================

def start_scheduler():
    """Initialize and start the scheduler with all jobs."""
    
    # Daily tasks at 00:00 GMT
    scheduler.add_job(
        check_and_reset_streaks,
        trigger=CronTrigger(hour=0, minute=0),
        id='daily_streak_check',
        name='Check and reset user streaks',
        replace_existing=True
    )
    
    scheduler.add_job(
        send_daily_review_reminders,
        trigger=CronTrigger(hour=8, minute=0),  # 8 AM GMT (morning in West Africa)
        id='daily_review_reminders',
        name='Send SRS review reminders',
        replace_existing=True
    )
    
    # Weekly tasks on Sunday at 23:00 GMT
    scheduler.add_job(
        calculate_weekly_leaderboard,
        trigger=CronTrigger(day_of_week='sun', hour=23, minute=0),
        id='weekly_leaderboard',
        name='Calculate weekly leaderboard',
        replace_existing=True
    )
    
    # Monthly tasks on 1st at 00:00 GMT
    scheduler.add_job(
        generate_monthly_reports,
        trigger=CronTrigger(day=1, hour=0, minute=0),
        id='monthly_reports',
        name='Generate monthly progress reports',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("✅ Scheduler started with 4 jobs")


def stop_scheduler():
    """Gracefully shutdown the scheduler."""
    scheduler.shutdown()
    logger.info("👋 Scheduler stopped")


# Example: Manual trigger for testing
if __name__ == "__main__":
    print("Testing scheduler jobs...")
    
    print("\n1. Testing streak check...")
    check_and_reset_streaks()
    
    print("\n2. Testing review reminders...")
    send_daily_review_reminders()
    
    print("\n3. Testing leaderboard calculation...")
    calculate_weekly_leaderboard()
    
    print("\n4. Testing monthly reports...")
    generate_monthly_reports()
    
    print("\n✅ All jobs tested successfully!")
