"""
Admin API endpoints - System monitoring and management.

This is for the Base10 team to monitor application health, user activity,
content quality, and system performance. Protected by admin role.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case, desc, Integer, text
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum

from app.db.session import get_db
from app.models.user import User
from app.models.question import Question
from app.models.enums import Subject, DifficultyLevel
from app.models.progress import Attempt
from app.models.classroom import Classroom, Assignment
from app.models.report import QuestionReport, ReportReason
from app.models.flashcard import FlashcardDeck, Flashcard, FlashcardReview
from app.core.security import get_current_user

router = APIRouter()


# ============= Auth & Permissions =============

def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Verify user has admin role."""
    from app.core.rbac import UserRole, is_admin
    
    # Check if user has admin role
    if not is_admin(current_user):
        # Fallback to email whitelist for legacy admin accounts
        LEGACY_ADMIN_EMAILS = [
            "cjalloh25@gmail.com",
            "esjallow03@gmail.com",
        ]
        
        if current_user.email not in LEGACY_ADMIN_EMAILS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required. Please contact system administrator."
            )
    
    return current_user


# ============= Schemas =============

class SystemHealth(BaseModel):
    """Overall system health metrics."""
    status: str = Field(..., description="healthy, degraded, or critical")
    timestamp: datetime
    database_connected: bool
    redis_connected: bool
    total_users: int
    active_users_24h: int
    active_users_7d: int
    total_questions: int
    total_attempts: int
    average_accuracy: float
    error_rate: float = Field(..., description="Percentage of failed requests")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-12-16T10:00:00Z",
                "database_connected": True,
                "redis_connected": True,
                "total_users": 1250,
                "active_users_24h": 420,
                "active_users_7d": 850,
                "total_questions": 700,
                "total_attempts": 85000,
                "average_accuracy": 68.5,
                "error_rate": 0.02
            }
        }


class UserGrowth(BaseModel):
    """User registration and engagement trends."""
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int
    retention_rate_7d: float = Field(..., description="% of users active after 7 days")
    retention_rate_30d: float
    churn_rate: float = Field(..., description="% of users inactive for >30 days")
    average_session_duration_minutes: float
    daily_active_users: int
    monthly_active_users: int


class ContentQuality(BaseModel):
    """Content quality and engagement metrics."""
    total_questions: int
    questions_by_subject: Dict[str, int]
    questions_by_difficulty: Dict[str, int]
    flagged_questions: int = Field(..., description="Questions with >3 reports")
    low_quality_questions: int = Field(..., description="Questions with <40% accuracy")
    high_quality_questions: int = Field(..., description="Questions with 60-80% accuracy")
    total_reports: int
    pending_reports: int


class EngagementMetrics(BaseModel):
    """User engagement and activity metrics."""
    total_attempts_today: int
    total_attempts_this_week: int
    average_attempts_per_user: float
    average_study_time_minutes: float
    users_with_streaks: int
    longest_current_streak: int
    questions_per_session: float
    completion_rate: float = Field(..., description="% of started sessions completed")


class TopUser(BaseModel):
    """Top performing user."""
    user_id: int
    email: Optional[str]
    phone_number: Optional[str]
    full_name: Optional[str]
    total_attempts: int
    accuracy: float
    study_streak: int
    total_points: int
    level: int
    last_active: datetime


class ProblemQuestion(BaseModel):
    """Question flagged for review."""
    question_id: int
    subject: str
    topic: str
    difficulty: str
    accuracy_rate: float
    total_attempts: int
    report_count: int
    reasons: List[str] = Field(..., description="Report reasons")


class PerformanceMetrics(BaseModel):
    """System performance metrics."""
    average_response_time_ms: float
    p95_response_time_ms: float
    requests_per_minute: float
    error_count_24h: int
    slow_queries_count: int = Field(..., description="Queries >1s")
    database_size_mb: float
    active_connections: int


class TimeRange(str, Enum):
    """Time range for analytics."""
    TODAY = "today"
    WEEK = "week"
    MONTH = "month"
    ALL_TIME = "all_time"


# ============= Dashboard Endpoints =============

@router.get("/health", response_model=SystemHealth)
async def get_system_health(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Get overall system health status.
    
    Critical metrics for monitoring application health and identifying issues.
    """
    # Count users
    total_users = db.query(func.count(User.id)).scalar() or 0
    
    # Active users in last 24 hours
    day_ago = datetime.now(timezone.utc) - timedelta(days=1)
    active_24h = db.query(func.count(func.distinct(User.id))).filter(
        User.last_activity_date >= day_ago
    ).scalar() or 0
    
    # Active users in last 7 days
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    active_7d = db.query(func.count(func.distinct(User.id))).filter(
        User.last_activity_date >= week_ago
    ).scalar() or 0
    
    # Question and attempt stats
    total_questions = db.query(func.count(Question.id)).scalar() or 0
    total_attempts = db.query(func.count(Attempt.id)).scalar() or 0
    
    # Calculate average accuracy
    accuracy_query = db.query(
        func.avg(case((Attempt.is_correct == True, 100), else_=0))
    ).scalar()
    average_accuracy = round(accuracy_query or 0, 2)
    
    # Check database connection
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except:
        db_connected = False
    
    # Check Redis connection (optional)
    redis_connected = False
    try:
        from app.core.redis_client import RedisClient
        redis_client = RedisClient()
        if redis_client.client:
            redis_client.client.ping()
            redis_connected = True
    except:
        redis_connected = False
    
    # Determine health status
    if not db_connected or active_24h < 10:
        health_status = "critical"
    elif redis_connected and active_24h > 50:
        health_status = "healthy"
    else:
        health_status = "degraded"
    
    return SystemHealth(
        status=health_status,
        timestamp=datetime.now(timezone.utc),
        database_connected=db_connected,
        redis_connected=redis_connected,
        total_users=total_users,
        active_users_24h=active_24h,
        active_users_7d=active_7d,
        total_questions=total_questions,
        total_attempts=total_attempts,
        average_accuracy=average_accuracy,
        error_rate=0.0  # TODO: Implement error tracking
    )


@router.get("/users/growth", response_model=UserGrowth)
async def get_user_growth(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Get user growth and retention metrics.
    
    Track new registrations, retention rates, and churn.
    """
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)
    
    # New users
    new_today = db.query(func.count(User.id)).filter(
        User.created_at >= today_start
    ).scalar() or 0
    
    new_week = db.query(func.count(User.id)).filter(
        User.created_at >= week_start
    ).scalar() or 0
    
    new_month = db.query(func.count(User.id)).filter(
        User.created_at >= month_start
    ).scalar() or 0
    
    # Retention: Users created 7 days ago who were active in last 24h
    seven_days_ago_start = (now - timedelta(days=7)).replace(hour=0, minute=0, second=0)
    seven_days_ago_end = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0)
    
    users_created_7d_ago = db.query(func.count(User.id)).filter(
        and_(
            User.created_at >= seven_days_ago_start,
            User.created_at < seven_days_ago_end
        )
    ).scalar() or 1  # Avoid division by zero
    
    retained_7d = db.query(func.count(User.id)).filter(
        and_(
            User.created_at >= seven_days_ago_start,
            User.created_at < seven_days_ago_end,
            User.last_activity_date >= now - timedelta(days=1)
        )
    ).scalar() or 0
    
    retention_7d = (retained_7d / users_created_7d_ago * 100) if users_created_7d_ago > 0 else 0
    
    # 30-day retention
    thirty_days_ago_start = (now - timedelta(days=30)).replace(hour=0, minute=0, second=0)
    thirty_days_ago_end = (now - timedelta(days=29)).replace(hour=0, minute=0, second=0)
    
    users_created_30d_ago = db.query(func.count(User.id)).filter(
        and_(
            User.created_at >= thirty_days_ago_start,
            User.created_at < thirty_days_ago_end
        )
    ).scalar() or 1
    
    retained_30d = db.query(func.count(User.id)).filter(
        and_(
            User.created_at >= thirty_days_ago_start,
            User.created_at < thirty_days_ago_end,
            User.last_activity_date >= now - timedelta(days=7)
        )
    ).scalar() or 0
    
    retention_30d = (retained_30d / users_created_30d_ago * 100) if users_created_30d_ago > 0 else 0
    
    # Churn rate: Users inactive for >30 days
    total_users = db.query(func.count(User.id)).scalar() or 1
    inactive_users = db.query(func.count(User.id)).filter(
        or_(
            User.last_activity_date < month_start,
            User.last_activity_date.is_(None)
        )
    ).scalar() or 0
    
    churn_rate = (inactive_users / total_users * 100) if total_users > 0 else 0
    
    # DAU and MAU
    dau = db.query(func.count(func.distinct(User.id))).filter(
        User.last_activity_date >= today_start
    ).scalar() or 0
    
    mau = db.query(func.count(func.distinct(User.id))).filter(
        User.last_activity_date >= month_start
    ).scalar() or 0
    
    # Average session duration (estimate from attempts)
    avg_session = db.query(
        func.avg(Attempt.time_taken_ms)
    ).filter(
        Attempt.time_taken_ms.isnot(None)
    ).scalar() or 0
    
    avg_session_minutes = (avg_session / 1000 / 60) if avg_session > 0 else 0
    
    return UserGrowth(
        new_users_today=new_today,
        new_users_this_week=new_week,
        new_users_this_month=new_month,
        retention_rate_7d=round(retention_7d, 2),
        retention_rate_30d=round(retention_30d, 2),
        churn_rate=round(churn_rate, 2),
        average_session_duration_minutes=round(avg_session_minutes, 2),
        daily_active_users=dau,
        monthly_active_users=mau
    )


@router.get("/content/quality", response_model=ContentQuality)
async def get_content_quality(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Get content quality metrics.
    
    Identify problematic questions that need review or removal.
    """
    # Total questions
    total_questions = db.query(func.count(Question.id)).scalar() or 0
    
    # Questions by subject - use raw query to avoid enum mismatch
    subject_breakdown = {}
    subject_counts = db.query(
        Question.subject,
        func.count(Question.id).label('count')
    ).group_by(Question.subject).all()
    
    for subject, count in subject_counts:
        subject_breakdown[subject.value if hasattr(subject, 'value') else str(subject)] = count
    
    # Questions by difficulty
    difficulty_breakdown = {}
    difficulty_counts = db.query(
        Question.difficulty,
        func.count(Question.id).label('count')
    ).group_by(Question.difficulty).all()
    
    for difficulty, count in difficulty_counts:
        difficulty_breakdown[difficulty.value if hasattr(difficulty, 'value') else str(difficulty)] = count
    
    # Flagged questions (>3 reports)
    flagged_subquery = db.query(
        QuestionReport.question_id
    ).filter(
        QuestionReport.status == "pending"
    ).group_by(QuestionReport.question_id).having(
        func.count(QuestionReport.id) > 3
    ).subquery()
    
    flagged = db.query(func.count(flagged_subquery.c.question_id)).scalar() or 0
    
    # Low quality questions (<40% accuracy)
    low_quality_subquery = db.query(
        Attempt.question_id
    ).group_by(Attempt.question_id).having(
        func.avg(case((Attempt.is_correct == True, 1), else_=0)) < 0.4
    ).subquery()
    
    low_quality = db.query(func.count(low_quality_subquery.c.question_id)).scalar() or 0
    
    # High quality questions (60-80% accuracy - ideal range)
    high_quality_subquery = db.query(
        Attempt.question_id
    ).group_by(Attempt.question_id).having(
        and_(
            func.avg(case((Attempt.is_correct == True, 1), else_=0)) >= 0.6,
            func.avg(case((Attempt.is_correct == True, 1), else_=0)) <= 0.8
        )
    ).subquery()
    
    high_quality = db.query(func.count(high_quality_subquery.c.question_id)).scalar() or 0
    
    # Report stats
    total_reports = db.query(func.count(QuestionReport.id)).scalar() or 0
    pending_reports = db.query(func.count(QuestionReport.id)).filter(
        QuestionReport.status == "pending"
    ).scalar() or 0
    
    return ContentQuality(
        total_questions=total_questions,
        questions_by_subject=subject_breakdown,
        questions_by_difficulty=difficulty_breakdown,
        flagged_questions=flagged,
        low_quality_questions=low_quality,
        high_quality_questions=high_quality,
        total_reports=total_reports,
        pending_reports=pending_reports
    )


@router.get("/engagement", response_model=EngagementMetrics)
async def get_engagement_metrics(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Get user engagement metrics.
    
    Track how actively users are engaging with the platform.
    """
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    
    # Attempts today and this week
    attempts_today = db.query(func.count(Attempt.id)).filter(
        Attempt.attempted_at >= today_start
    ).scalar() or 0
    
    attempts_week = db.query(func.count(Attempt.id)).filter(
        Attempt.attempted_at >= week_start
    ).scalar() or 0
    
    # Average attempts per user
    total_users = db.query(func.count(User.id)).scalar() or 1
    total_attempts = db.query(func.count(Attempt.id)).scalar() or 0
    avg_attempts = total_attempts / total_users if total_users > 0 else 0
    
    # Average study time
    avg_time_ms = db.query(func.avg(Attempt.time_taken_ms)).filter(
        Attempt.time_taken_ms.isnot(None)
    ).scalar() or 0
    avg_study_time = (avg_time_ms / 1000 / 60) if avg_time_ms > 0 else 0
    
    # Users with active streaks
    users_with_streaks = db.query(func.count(User.id)).filter(
        User.study_streak > 0
    ).scalar() or 0
    
    # Longest current streak
    longest_streak = db.query(func.max(User.study_streak)).scalar() or 0
    
    # Questions per session (estimate)
    sessions = db.query(
        func.count(func.distinct(func.date(Attempt.attempted_at)))
    ).scalar() or 1
    questions_per_session = total_attempts / sessions if sessions > 0 else 0
    
    # Completion rate (users who answered >10 questions)
    engaged_users = db.query(func.count(func.distinct(Attempt.user_id))).group_by(
        Attempt.user_id
    ).having(func.count(Attempt.id) > 10).scalar() or 0
    
    completion_rate = (engaged_users / total_users * 100) if total_users > 0 else 0
    
    return EngagementMetrics(
        total_attempts_today=attempts_today,
        total_attempts_this_week=attempts_week,
        average_attempts_per_user=round(avg_attempts, 2),
        average_study_time_minutes=round(avg_study_time, 2),
        users_with_streaks=users_with_streaks,
        longest_current_streak=longest_streak,
        questions_per_session=round(questions_per_session, 2),
        completion_rate=round(completion_rate, 2)
    )


@router.get("/users/top", response_model=List[TopUser])
async def get_top_users(
    limit: int = Query(default=10, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Get top performing users.
    
    Identify power users for case studies, testimonials, or rewards.
    """
    # Get users with most attempts
    top_users_query = db.query(
        User.id,
        User.email,
        User.phone_number,
        User.full_name,
        User.study_streak,
        User.total_points,
        User.level,
        User.last_activity_date,
        func.count(Attempt.id).label('total_attempts'),
        func.avg(case((Attempt.is_correct == True, 100), else_=0)).label('accuracy')
    ).join(
        Attempt, User.id == Attempt.user_id
    ).group_by(
        User.id
    ).order_by(
        desc('total_attempts')
    ).limit(limit).all()
    
    top_users = []
    for user_data in top_users_query:
        top_users.append(TopUser(
            user_id=user_data.id,
            email=user_data.email,
            phone_number=user_data.phone_number,
            full_name=user_data.full_name,
            total_attempts=user_data.total_attempts,
            accuracy=round(user_data.accuracy or 0, 2),
            study_streak=user_data.study_streak or 0,
            total_points=user_data.total_points or 0,
            level=user_data.level or 1,
            last_active=user_data.last_activity_date or datetime.now(timezone.utc)
        ))
    
    return top_users


@router.get("/questions/problematic", response_model=List[ProblemQuestion])
async def get_problematic_questions(
    min_attempts: int = Query(default=50, description="Minimum attempts to qualify"),
    max_accuracy: float = Query(default=0.4, description="Maximum accuracy rate"),
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Get questions flagged as problematic.
    
    Questions with low accuracy or multiple reports need review.
    """
    # Get questions with low accuracy
    low_accuracy_questions = db.query(
        Question.id,
        Question.subject,
        Question.topic,
        Question.difficulty,
        func.count(Attempt.id).label('total_attempts'),
        func.avg(case((Attempt.is_correct == True, 1), else_=0)).label('accuracy')
    ).join(
        Attempt, Question.id == Attempt.question_id
    ).group_by(
        Question.id
    ).having(
        and_(
            func.count(Attempt.id) >= min_attempts,
            func.avg(case((Attempt.is_correct == True, 1), else_=0)) <= max_accuracy
        )
    ).order_by(
        'accuracy'
    ).limit(limit).all()
    
    problem_questions = []
    for q in low_accuracy_questions:
        # Get report count and reasons
        report_count = db.query(func.count(QuestionReport.id)).filter(
            QuestionReport.question_id == q.id
        ).scalar() or 0
        
        # Get unique reasons
        report_reasons = db.query(QuestionReport.reason).filter(
            QuestionReport.question_id == q.id
        ).distinct().all()
        
        reasons = [r[0].value if hasattr(r[0], 'value') else str(r[0]) for r in report_reasons]
        
        problem_questions.append(ProblemQuestion(
            question_id=q.id,
            subject=q.subject.value,
            topic=q.topic,
            difficulty=q.difficulty.value,
            accuracy_rate=round(q.accuracy * 100, 2),
            total_attempts=q.total_attempts,
            report_count=report_count,
            reasons=reasons
        ))
    
    return problem_questions


@router.get("/stats/summary")
async def get_stats_summary(
    time_range: TimeRange = Query(default=TimeRange.WEEK),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Get comprehensive statistics summary.
    
    One-stop dashboard for all key metrics.
    """
    # Calculate time filter
    now = datetime.now(timezone.utc)
    if time_range == TimeRange.TODAY:
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif time_range == TimeRange.WEEK:
        start_date = now - timedelta(days=7)
    elif time_range == TimeRange.MONTH:
        start_date = now - timedelta(days=30)
    else:  # ALL_TIME
        start_date = datetime(2020, 1, 1, tzinfo=timezone.utc)
    
    # User stats
    total_users = db.query(func.count(User.id)).scalar() or 0
    verified_users = db.query(func.count(User.id)).filter(User.is_verified == True).scalar() or 0
    
    # Activity stats
    total_attempts = db.query(func.count(Attempt.id)).filter(
        Attempt.attempted_at >= start_date
    ).scalar() or 0
    
    unique_active_users = db.query(func.count(func.distinct(Attempt.user_id))).filter(
        Attempt.attempted_at >= start_date
    ).scalar() or 0
    
    # Classroom stats
    total_classrooms = db.query(func.count(Classroom.id)).scalar() or 0
    total_teachers = db.query(func.count(func.distinct(Classroom.teacher_id))).scalar() or 0
    
    # Content stats
    total_questions = db.query(func.count(Question.id)).scalar() or 0
    total_flashcard_decks = db.query(func.count(FlashcardDeck.id)).scalar() or 0
    
    # Engagement
    avg_accuracy = db.query(
        func.avg(case((Attempt.is_correct == True, 100), else_=0))
    ).filter(Attempt.attempted_at >= start_date).scalar() or 0
    
    # Report stats
    pending_reports = db.query(func.count(QuestionReport.id)).filter(
        QuestionReport.status == "pending"
    ).scalar() or 0
    
    return {
        "time_range": time_range.value,
        "timestamp": now.isoformat(),
        "users": {
            "total": total_users,
            "verified": verified_users,
            "verification_rate": round((verified_users / total_users * 100) if total_users > 0 else 0, 2),
            "active_in_period": unique_active_users
        },
        "activity": {
            "total_attempts": total_attempts,
            "average_accuracy": round(avg_accuracy, 2),
            "attempts_per_active_user": round((total_attempts / unique_active_users) if unique_active_users > 0 else 0, 2)
        },
        "classrooms": {
            "total": total_classrooms,
            "total_teachers": total_teachers,
            "avg_students_per_classroom": round((unique_active_users / total_classrooms) if total_classrooms > 0 else 0, 2)
        },
        "content": {
            "total_questions": total_questions,
            "total_flashcard_decks": total_flashcard_decks,
            "pending_reports": pending_reports
        }
    }


# ============= User Management =============

@router.get("/users")
async def list_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Get a paginated list of all users.
    
    For the admin user management page.
    """
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
        
    total = query.count()
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "users": [{
            "id": u.id,
            "email": u.email,
            "phone_number": u.phone_number,
            "full_name": u.full_name,
            "role": u.role,
            "is_verified": u.is_verified,
            "is_active": u.is_active,
            "created_at": u.created_at,
            "last_activity_date": u.last_activity_date,
            "study_streak": u.study_streak,
            "total_points": u.total_points,
            "level": u.level
        } for u in users]
    }


@router.get("/users/search")
async def search_users(
    query: str = Query(..., min_length=3, description="Email, phone, or name"),
    limit: int = Query(default=10, le=50),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Search for users by email, phone, or name.
    
    For support and debugging purposes.
    """
    search_pattern = f"%{query}%"
    
    users = db.query(User).filter(
        or_(
            User.email.ilike(search_pattern),
            User.phone_number.ilike(search_pattern),
            User.full_name.ilike(search_pattern)
        )
    ).limit(limit).all()
    
    return [{
        "id": u.id,
        "email": u.email,
        "phone_number": u.phone_number,
        "full_name": u.full_name,
        "role": u.role,
        "is_verified": u.is_verified,
        "is_active": u.is_active,
        "created_at": u.created_at,
        "last_activity_date": u.last_activity_date,
        "study_streak": u.study_streak,
        "total_points": u.total_points,
        "level": u.level
    } for u in users]


@router.put("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    reason: str = Query(..., description="Reason for deactivation"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Deactivate a user account.
    
    For handling abuse, spam, or user requests.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = False
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    # TODO: Log the action with reason in an audit log
    return {"status": "success", "message": f"User {user_id} deactivated", "reason": reason}


@router.put("/users/{user_id}")
async def update_user_details(
    user_id: int,
    data: schemas.UserUpdateAdmin,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Update user details (Admin only).
    
    Allows changing role, status, points, and profile info.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = data.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(user, key, value)
    
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    
    return {
        "status": "success",
        "message": f"User {user_id} updated",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "total_points": user.total_points
        }
    }


@router.put("/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Reactivate a deactivated user account."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = True
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    return {
        "message": "User activated successfully",
        "user_id": user_id,
        "activated_by": admin.email,
        "timestamp": datetime.now(timezone.utc)
    }


# ============= Content Management =============

@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: int,
    reason: str = Query(..., description="Reason for deletion"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Delete a problematic question.
    
    For removing incorrect, inappropriate, or low-quality content.
    """
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Soft delete or hard delete based on preference
    db.delete(question)
    db.commit()
    
    # TODO: Log deletion in audit log
    
    return {
        "message": "Question deleted successfully",
        "question_id": question_id,
        "reason": reason,
        "deleted_by": admin.email,
        "timestamp": datetime.now(timezone.utc)
    }


@router.put("/reports/{report_id}/resolve")
async def resolve_report(
    report_id: int,
    action: str = Query(..., description="Action taken: dismissed, question_fixed, question_deleted"),
    notes: Optional[str] = Query(None, description="Admin notes"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Resolve a question report.
    
    Mark as reviewed and take appropriate action.
    """
    report = db.query(QuestionReport).filter(QuestionReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report.status = "resolved"
    report.reviewed_by = admin.id
    report.reviewed_at = datetime.now(timezone.utc)
    report.admin_notes = f"{action}: {notes}" if notes else action
    
    db.commit()
    
    return {
        "message": "Report resolved successfully",
        "report_id": report_id,
        "action": action,
        "resolved_by": admin.email,
        "timestamp": datetime.now(timezone.utc)
    }


# ============= User Role Management =============

class RoleChangeRequest(BaseModel):
    """Request to change user role."""
    new_role: str
    reason: Optional[str] = None


@router.post("/admin/users/{user_id}/role")
async def change_user_role(
    user_id: int,
    role_data: RoleChangeRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Change a user's role (admin only).
    
    Use cases:
    - Promote student to teacher
    - Grant admin access
    - Demote user if needed
    """
    from app.core.rbac import UserRole
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Validate role
    valid_roles = [r.value for r in UserRole]
    if role_data.new_role not in valid_roles:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    # Get target user
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent self-demotion from admin
    if admin.id == target_user.id and target_user.role == UserRole.ADMIN.value and role_data.new_role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=400,
            detail="Cannot remove your own admin privileges"
        )
    
    old_role = target_user.role
    target_user.role = role_data.new_role
    db.commit()
    
    logger.info(
        f"🔐 Admin {admin.id} ({admin.email}) changed user {user_id} ({target_user.email or target_user.phone_number}) "
        f"role from '{old_role}' to '{role_data.new_role}'. Reason: {role_data.reason or 'Not provided'}"
    )
    
    return {
        "message": "Role updated successfully",
        "user_id": user_id,
        "user_email": target_user.email or target_user.phone_number,
        "old_role": old_role,
        "new_role": role_data.new_role,
        "changed_by": admin.email
    }


@router.get("/admin/users/by-role/{role}")
async def list_users_by_role(
    role: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """List all users with a specific role."""
    from app.core.rbac import UserRole
    
    valid_roles = [r.value for r in UserRole]
    if role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}")
    
    users = db.query(User).filter(User.role == role).offset(skip).limit(limit).all()
    
    return {
        "role": role,
        "total": db.query(func.count(User.id)).filter(User.role == role).scalar(),
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "phone_number": u.phone_number,
                "username": u.username,
                "full_name": u.full_name,
                "is_verified": u.is_verified,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "last_login": u.last_login.isoformat() if u.last_login else None
            }
            for u in users
        ]
    }


@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Delete a user account (admin only).
    
    This is a hard delete. Use with caution.
    Related data (attempts, classrooms, etc.) will be handled by database cascade rules.
    """
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Prevent self-deletion
    if admin.id == user_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete your own account"
        )
    
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Store info for logging before deletion
    user_identifier = target_user.email or target_user.phone_number or target_user.username
    user_role = target_user.role
    
    # Delete user (cascade will handle related records)
    db.delete(target_user)
    db.commit()
    
    logger.warning(
        f"🗑️  Admin {admin.id} ({admin.email}) deleted user {user_id} "
        f"({user_identifier}, role: {user_role})"
    )
    
    return {
        "message": "User deleted successfully",
        "user_id": user_id,
        "user_identifier": user_identifier,
        "deleted_by": admin.email
    }

