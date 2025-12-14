"""Student dashboard and analytics endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case, Integer
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from enum import Enum
import json

from app.db.session import get_db
from app.models.user import User
from app.models.question import Question, Subject, DifficultyLevel
from app.models.progress import Attempt
from app.models.classroom import Classroom, classroom_students
from app.api.v1.auth import get_current_user

router = APIRouter()


class TimeRange(str, Enum):
    """Time range for analytics."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ALL_TIME = "all_time"


class MasteryLevel(str, Enum):
    """Topic mastery levels."""
    BEGINNER = "beginner"  # < 40% accuracy
    DEVELOPING = "developing"  # 40-60%
    PROFICIENT = "proficient"  # 60-80%
    EXPERT = "expert"  # > 80%


def _calculate_mastery_level(accuracy: float) -> MasteryLevel:
    """Calculate mastery level from accuracy percentage."""
    if accuracy < 40:
        return MasteryLevel.BEGINNER
    elif accuracy < 60:
        return MasteryLevel.DEVELOPING
    elif accuracy < 80:
        return MasteryLevel.PROFICIENT
    else:
        return MasteryLevel.EXPERT


def _get_time_range_filter(time_range: TimeRange):
    """Get datetime filter for time range."""
    now = datetime.utcnow()
    
    if time_range == TimeRange.DAILY:
        return now - timedelta(days=1)
    elif time_range == TimeRange.WEEKLY:
        return now - timedelta(weeks=1)
    elif time_range == TimeRange.MONTHLY:
        return now - timedelta(days=30)
    else:  # ALL_TIME
        return datetime(2020, 1, 1)  # Beginning of time for this app


def _calculate_performance_trends(db: Session, user_id: int) -> Dict:
    """Calculate performance trends over different time periods."""
    trends = {}
    
    for time_range in [TimeRange.DAILY, TimeRange.WEEKLY, TimeRange.MONTHLY]:
        start_date = _get_time_range_filter(time_range)
        
        stats = db.query(
            func.count(Attempt.id).label('total'),
            func.sum(case((Attempt.is_correct == True, 1), else_=0)).label('correct')
        ).filter(
            and_(
                Attempt.user_id == user_id,
                Attempt.attempted_at >= start_date
            )
        ).first()
        
        total = stats.total or 0
        correct = stats.correct or 0
        accuracy = (correct / total * 100) if total > 0 else 0
        
        trends[time_range.value] = {
            'attempts': total,
            'correct': correct,
            'accuracy': round(accuracy, 2)
        }
    
    return trends


def _calculate_topic_mastery(db: Session, user_id: int) -> List[Dict]:
    """Calculate mastery level for each topic."""
    topic_stats = db.query(
        Question.topic,
        Question.subject,
        func.count(Attempt.id).label('attempts'),
        func.sum(case((Attempt.is_correct == True, 1), else_=0)).label('correct')
    ).join(
        Attempt, Attempt.question_id == Question.id
    ).filter(
        Attempt.user_id == user_id
    ).group_by(
        Question.topic, Question.subject
    ).all()
    
    mastery_data = []
    for topic, subject, attempts, correct in topic_stats:
        correct = correct or 0
        accuracy = (correct / attempts * 100) if attempts > 0 else 0
        mastery_level = _calculate_mastery_level(accuracy)
        
        mastery_data.append({
            'topic': topic,
            'subject': subject.value,
            'attempts': attempts,
            'correct': correct,
            'accuracy': round(accuracy, 2),
            'mastery_level': mastery_level.value,
            'needs_practice': accuracy < 70  # Flag topics needing work
        })
    
    # Sort by accuracy (weakest first)
    mastery_data.sort(key=lambda x: x['accuracy'])
    
    return mastery_data


def _calculate_exam_readiness(db: Session, user_id: int, current_user: User) -> Dict:
    """Calculate exam readiness score and breakdown."""
    # Get overall stats
    overall_stats = db.query(
        func.count(Attempt.id).label('total'),
        func.sum(case((Attempt.is_correct == True, 1), else_=0)).label('correct')
    ).filter(
        Attempt.user_id == user_id
    ).first()
    
    total_attempts = overall_stats.total or 0
    total_correct = overall_stats.correct or 0
    overall_accuracy = (total_correct / total_attempts * 100) if total_attempts > 0 else 0
    
    # Calculate readiness factors
    readiness_factors = {
        'overall_accuracy': overall_accuracy,
        'total_practice': min(total_attempts / 500 * 100, 100),  # 500 questions = 100%
        'topic_coverage': 0,  # Calculated below
        'consistency': 0,  # Based on streak
        'recent_performance': 0  # Last 7 days
    }
    
    # Topic coverage (how many topics attempted)
    topics_attempted = db.query(
        func.count(func.distinct(Question.topic))
    ).join(
        Attempt, Attempt.question_id == Question.id
    ).filter(
        Attempt.user_id == user_id
    ).scalar() or 0
    
    total_topics = db.query(func.count(func.distinct(Question.topic))).scalar() or 1
    readiness_factors['topic_coverage'] = (topics_attempted / total_topics * 100)
    
    # Consistency (streak days)
    streak_days = _calculate_streak(db, user_id)
    readiness_factors['consistency'] = min(streak_days / 30 * 100, 100)  # 30 days = 100%
    
    # Recent performance (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_stats = db.query(
        func.count(Attempt.id).label('total'),
        func.sum(case((Attempt.is_correct == True, 1), else_=0)).label('correct')
    ).filter(
        and_(
            Attempt.user_id == user_id,
            Attempt.attempted_at >= week_ago
        )
    ).first()
    
    recent_total = recent_stats.total or 0
    recent_correct = recent_stats.correct or 0
    recent_accuracy = (recent_correct / recent_total * 100) if recent_total > 0 else 0
    readiness_factors['recent_performance'] = recent_accuracy
    
    # Calculate weighted readiness score
    weights = {
        'overall_accuracy': 0.35,
        'total_practice': 0.25,
        'topic_coverage': 0.20,
        'consistency': 0.10,
        'recent_performance': 0.10
    }
    
    readiness_score = sum(
        readiness_factors[factor] * weight 
        for factor, weight in weights.items()
    )
    
    # Determine readiness level
    if readiness_score >= 80:
        readiness_level = "ready"
        message = "Excellent! You're well-prepared for the exam."
    elif readiness_score >= 60:
        readiness_level = "almost_ready"
        message = "Good progress! Focus on weak topics to improve."
    elif readiness_score >= 40:
        readiness_level = "needs_work"
        message = "Keep practicing! You need more preparation."
    else:
        readiness_level = "not_ready"
        message = "Start preparing now. Focus on understanding core concepts."
    
    # Days until exam
    days_until_exam = None
    if current_user.target_exam_date:
        days_until_exam = (current_user.target_exam_date - datetime.utcnow()).days
    
    return {
        'readiness_score': round(readiness_score, 2),
        'readiness_level': readiness_level,
        'message': message,
        'factors': {k: round(v, 2) for k, v in readiness_factors.items()},
        'days_until_exam': days_until_exam,
        'total_attempts': total_attempts
    }


def _generate_study_recommendations(
    db: Session, 
    user_id: int, 
    topic_mastery: List[Dict],
    exam_readiness: Dict
) -> List[Dict]:
    """Generate personalized study recommendations."""
    recommendations = []
    
    # 1. Focus on weak topics
    weak_topics = [t for t in topic_mastery if t['accuracy'] < 70]
    if weak_topics:
        top_weak = weak_topics[:3]  # Top 3 weakest
        recommendations.append({
            'priority': 'high',
            'type': 'weak_topics',
            'title': 'Strengthen Weak Topics',
            'message': f"Focus on: {', '.join([t['topic'] for t in top_weak])}",
            'action': 'practice_topics',
            'data': [t['topic'] for t in top_weak]
        })
    
    # 2. Spaced repetition reminders
    due_reviews = db.query(func.count(Attempt.id)).filter(
        and_(
            Attempt.user_id == user_id,
            Attempt.next_review_date <= datetime.utcnow()
        )
    ).scalar() or 0
    
    if due_reviews > 0:
        recommendations.append({
            'priority': 'high',
            'type': 'spaced_repetition',
            'title': 'Review Due Questions',
            'message': f"You have {due_reviews} questions ready for review",
            'action': 'start_review',
            'data': {'count': due_reviews}
        })
    
    # 3. Consistency boost
    streak = _calculate_streak(db, user_id)
    if streak == 0:
        recommendations.append({
            'priority': 'medium',
            'type': 'consistency',
            'title': 'Build Your Streak',
            'message': "Start a study streak! Practice daily to improve retention",
            'action': 'practice_daily',
            'data': {}
        })
    elif streak < 7:
        recommendations.append({
            'priority': 'low',
            'type': 'consistency',
            'title': f"Current Streak: {streak} days",
            'message': "Keep going! Consistency is key to success",
            'action': 'maintain_streak',
            'data': {'streak': streak}
        })
    
    # 4. Exam preparation urgency
    if exam_readiness['days_until_exam']:
        days = exam_readiness['days_until_exam']
        if days <= 30 and exam_readiness['readiness_score'] < 70:
            recommendations.append({
                'priority': 'high',
                'type': 'exam_urgency',
                'title': f"Exam in {days} days!",
                'message': "Intensify your preparation. Focus on core topics.",
                'action': 'intensive_practice',
                'data': {'days_remaining': days}
            })
    
    # 5. Explore new topics
    if exam_readiness['factors']['topic_coverage'] < 80:
        recommendations.append({
            'priority': 'medium',
            'type': 'coverage',
            'title': 'Explore More Topics',
            'message': "You've covered some topics well. Try new ones to broaden your knowledge.",
            'action': 'explore_topics',
            'data': {}
        })
    
    # Sort by priority
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    recommendations.sort(key=lambda x: priority_order[x['priority']])
    
    return recommendations


def _calculate_time_analytics(db: Session, user_id: int) -> Dict:
    """Calculate time-based analytics from psychometric data."""
    # Get attempts with time data
    time_stats = db.query(
        func.count(Attempt.id).label('total'),
        func.avg(Attempt.time_taken_ms).label('avg_time'),
        func.sum(Attempt.time_taken_ms).label('total_time')
    ).filter(
        and_(
            Attempt.user_id == user_id,
            Attempt.time_taken_ms.isnot(None)
        )
    ).first()
    
    total_attempts = time_stats.total or 0
    avg_time_ms = time_stats.avg_time or 0
    total_time_ms = time_stats.total_time or 0
    
    # Convert to minutes
    avg_time_seconds = avg_time_ms / 1000
    total_time_minutes = total_time_ms / 60000
    
    # Detect patterns
    guessing_count = db.query(func.count(Attempt.id)).filter(
        and_(
            Attempt.user_id == user_id,
            Attempt.time_taken_ms < 2000  # < 2 seconds = likely guessing
        )
    ).scalar() or 0
    
    struggling_count = db.query(func.count(Attempt.id)).filter(
        and_(
            Attempt.user_id == user_id,
            Attempt.time_taken_ms > 60000  # > 60 seconds = struggling
        )
    ).scalar() or 0
    
    return {
        'total_study_time_minutes': round(total_time_minutes, 2),
        'average_time_per_question_seconds': round(avg_time_seconds, 2),
        'total_questions_answered': total_attempts,
        'patterns': {
            'guessing_instances': guessing_count,
            'struggling_instances': struggling_count,
            'guessing_rate': round((guessing_count / total_attempts * 100) if total_attempts > 0 else 0, 2),
            'struggling_rate': round((struggling_count / total_attempts * 100) if total_attempts > 0 else 0, 2)
        }
    }


def _calculate_streak(db: Session, user_id: int) -> int:
    """Calculate current study streak in days."""
    # Get all unique dates with attempts (ordered desc)
    dates = db.query(
        func.date(Attempt.attempted_at).label('date')
    ).filter(
        Attempt.user_id == user_id
    ).distinct().order_by(
        func.date(Attempt.attempted_at).desc()
    ).limit(365).all()
    
    if not dates:
        return 0
    
    # Check if there's activity today or yesterday
    today = datetime.utcnow().date()
    if dates[0][0] not in [today, today - timedelta(days=1)]:
        return 0  # Streak broken
    
    # Count consecutive days
    streak = 1
    for i in range(len(dates) - 1):
        current = dates[i][0]
        next_date = dates[i + 1][0]
        if (current - next_date).days == 1:
            streak += 1
        else:
            break
    
    return streak


def _get_classmate_comparison(db: Session, user_id: int) -> Optional[Dict]:
    """Get comparison with classmates if student is enrolled."""
    # Find classrooms student is enrolled in
    classrooms = db.query(Classroom).join(
        classroom_students,
        classroom_students.c.classroom_id == Classroom.id
    ).filter(
        classroom_students.c.student_id == user_id
    ).all()
    
    if not classrooms:
        return None
    
    # Get all classmate IDs
    classmate_ids = []
    for classroom in classrooms:
        members = db.query(classroom_students.c.student_id).filter(
            classroom_students.c.classroom_id == classroom.id
        ).all()
        classmate_ids.extend([m[0] for m in members if m[0] != user_id])
    
    if not classmate_ids:
        return None
    
    # Calculate user's stats
    user_stats = db.query(
        func.count(Attempt.id).label('total'),
        func.sum(case((Attempt.is_correct == True, 1), else_=0)).label('correct')
    ).filter(
        Attempt.user_id == user_id
    ).first()
    
    user_total = user_stats.total or 0
    user_correct = user_stats.correct or 0
    user_accuracy = (user_correct / user_total * 100) if user_total > 0 else 0
    
    # Calculate class average
    class_stats = db.query(
        Attempt.user_id,
        func.count(Attempt.id).label('total'),
        func.sum(case((Attempt.is_correct == True, 1), else_=0)).label('correct')
    ).filter(
        Attempt.user_id.in_(classmate_ids)
    ).group_by(
        Attempt.user_id
    ).all()
    
    if not class_stats:
        return None
    
    # Calculate average accuracy
    classmate_accuracies = [
        (correct or 0) / total * 100 if total > 0 else 0
        for _, total, correct in class_stats
    ]
    
    class_avg_accuracy = sum(classmate_accuracies) / len(classmate_accuracies)
    
    # Ranking
    all_accuracies = classmate_accuracies + [user_accuracy]
    all_accuracies.sort(reverse=True)
    user_rank = all_accuracies.index(user_accuracy) + 1
    
    return {
        'enrolled': True,
        'classroom_count': len(classrooms),
        'classmate_count': len(classmate_ids),
        'your_accuracy': round(user_accuracy, 2),
        'class_average_accuracy': round(class_avg_accuracy, 2),
        'performance_vs_class': round(user_accuracy - class_avg_accuracy, 2),
        'your_rank': user_rank,
        'total_students': len(all_accuracies),
        'percentile': round((len(all_accuracies) - user_rank) / len(all_accuracies) * 100, 2)
    }


@router.get("/dashboard")
def get_student_dashboard(
    time_range: TimeRange = Query(default=TimeRange.WEEKLY, description="Time range for trends"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive student dashboard with all analytics.
    
    This endpoint provides students with a complete view of their learning progress:
    - Performance trends over time
    - Topic mastery levels
    - Exam readiness score
    - Personalized study recommendations
    - Time tracking analytics
    - Comparison with classmates (if enrolled)
    
    **Example Response:**
    ```json
    {
        "overview": {
            "total_attempts": 250,
            "overall_accuracy": 72.5,
            "streak_days": 12,
            "study_time_hours": 8.5
        },
        "performance_trends": {
            "daily": {"attempts": 15, "accuracy": 80.0},
            "weekly": {"attempts": 95, "accuracy": 75.0},
            "monthly": {"attempts": 250, "accuracy": 72.5}
        },
        "topic_mastery": [
            {
                "topic": "Algebra",
                "subject": "MATHEMATICS",
                "mastery_level": "proficient",
                "accuracy": 78.5,
                "needs_practice": false
            }
        ],
        "exam_readiness": {
            "readiness_score": 68.5,
            "readiness_level": "almost_ready",
            "days_until_exam": 45
        },
        "recommendations": [
            {
                "priority": "high",
                "title": "Strengthen Weak Topics",
                "message": "Focus on: Isotopes, Trigonometry"
            }
        ],
        "time_analytics": {
            "total_study_time_minutes": 510.5,
            "average_time_per_question_seconds": 22.3,
            "patterns": {
                "guessing_instances": 12,
                "guessing_rate": 4.8
            }
        },
        "classmate_comparison": {
            "your_accuracy": 72.5,
            "class_average_accuracy": 68.2,
            "your_rank": 5,
            "percentile": 75.0
        }
    }
    ```
    """
    # Calculate all analytics
    performance_trends = _calculate_performance_trends(db, current_user.id)
    topic_mastery = _calculate_topic_mastery(db, current_user.id)
    exam_readiness = _calculate_exam_readiness(db, current_user.id, current_user)
    time_analytics = _calculate_time_analytics(db, current_user.id)
    classmate_comparison = _get_classmate_comparison(db, current_user.id)
    
    # Generate personalized recommendations
    recommendations = _generate_study_recommendations(
        db, 
        current_user.id, 
        topic_mastery,
        exam_readiness
    )
    
    # Calculate streak
    streak_days = _calculate_streak(db, current_user.id)
    
    # Build overview
    all_time_stats = performance_trends.get('monthly', {})
    
    overview = {
        'total_attempts': all_time_stats.get('attempts', 0),
        'overall_accuracy': all_time_stats.get('accuracy', 0),
        'streak_days': streak_days,
        'study_time_hours': round(time_analytics['total_study_time_minutes'] / 60, 2)
    }
    
    return {
        'overview': overview,
        'performance_trends': performance_trends,
        'topic_mastery': topic_mastery,
        'exam_readiness': exam_readiness,
        'recommendations': recommendations,
        'time_analytics': time_analytics,
        'classmate_comparison': classmate_comparison,
        'last_updated': datetime.utcnow().isoformat()
    }


@router.get("/dashboard/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get quick dashboard summary for mobile app home screen.
    Lightweight version with key metrics only.
    """
    # Get basic stats
    stats = db.query(
        func.count(Attempt.id).label('total'),
        func.sum(case((Attempt.is_correct == True, 1), else_=0)).label('correct')
    ).filter(
        Attempt.user_id == current_user.id
    ).first()
    
    total = stats.total or 0
    correct = stats.correct or 0
    accuracy = (correct / total * 100) if total > 0 else 0
    
    # Get streak
    streak = _calculate_streak(db, current_user.id)
    
    # Get due reviews count
    due_reviews = db.query(func.count(Attempt.id)).filter(
        and_(
            Attempt.user_id == current_user.id,
            Attempt.next_review_date <= datetime.utcnow()
        )
    ).scalar() or 0
    
    # Get today's activity
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_attempts = db.query(func.count(Attempt.id)).filter(
        and_(
            Attempt.user_id == current_user.id,
            Attempt.attempted_at >= today_start
        )
    ).scalar() or 0
    
    return {
        'total_attempts': total,
        'overall_accuracy': round(accuracy, 2),
        'streak_days': streak,
        'due_reviews': due_reviews,
        'today_attempts': today_attempts,
        'has_target_exam': current_user.target_exam_date is not None
    }
