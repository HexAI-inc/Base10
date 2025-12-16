"""Offline sync API - The heart of the offline-first architecture."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, Integer
from datetime import datetime, timedelta
from typing import List, Dict
import json

from app.db.session import get_db
from app.models.user import User
from app.models.question import Question, Subject
from app.models.progress import Attempt
from app.schemas.schemas import (
    SyncPushRequest, SyncPushResponse,
    SyncPullRequest, SyncPullResponse,
    QuestionResponse, AttemptCreate
)
from app.api.v1.auth import get_current_user
from app.core.spaced_repetition import calculate_next_review_sm2, quality_from_attempt, should_review_question

router = APIRouter()


@router.post("/push", response_model=SyncPushResponse)
def sync_push_attempts(
    sync_data: SyncPushRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Push offline attempts to server.
    
    This is called when the student's phone reconnects to internet.
    Receives all quiz attempts made offline and saves them.
    
    Idempotency: Uses device_id + question_id + timestamp to prevent duplicates.
    """
    synced_count = 0
    failed_count = 0
    
    for attempt_data in sync_data.attempts:
        try:
            # Check for duplicate (same device, same question, same time)
            existing = db.query(Attempt).filter(
                and_(
                    Attempt.user_id == current_user.id,
                    Attempt.question_id == attempt_data.question_id,
                    Attempt.device_id == sync_data.device_id,
                    Attempt.attempted_at == attempt_data.attempted_at
                )
            ).first()
            
            if existing:
                continue  # Skip duplicate
            
            # Calculate SM-2 spaced repetition schedule
            quality = quality_from_attempt(attempt_data.is_correct)
            
            # Get previous attempt for this question to continue SRS chain
            previous_attempt = db.query(Attempt).filter(
                and_(
                    Attempt.user_id == current_user.id,
                    Attempt.question_id == attempt_data.question_id
                )
            ).order_by(Attempt.attempted_at.desc()).first()
            
            if previous_attempt:
                interval, ease, reps, next_date = calculate_next_review_sm2(
                    quality,
                    previous_attempt.srs_interval,
                    previous_attempt.srs_ease_factor,
                    previous_attempt.srs_repetitions
                )
            else:
                # First attempt
                interval, ease, reps, next_date = calculate_next_review_sm2(quality)
            
            # Create new attempt record with SRS data
            new_attempt = Attempt(
                user_id=current_user.id,
                question_id=attempt_data.question_id,
                is_correct=attempt_data.is_correct,
                selected_option=attempt_data.selected_option,
                attempted_at=attempt_data.attempted_at,
                device_id=sync_data.device_id,
                synced_at=datetime.utcnow(),
                # SRS fields
                srs_interval=interval,
                srs_ease_factor=ease,
                srs_repetitions=reps,
                next_review_date=next_date,
                # Psychometric fields
                time_taken_ms=attempt_data.time_taken_ms,
                confidence_level=attempt_data.confidence_level,
                network_type=attempt_data.network_type,
                app_version=attempt_data.app_version
            )
            
            db.add(new_attempt)
            synced_count += 1
            
        except Exception as e:
            failed_count += 1
            print(f"Failed to sync attempt: {e}")
    
    db.commit()
    
    return SyncPushResponse(
        status="success",
        synced_count=synced_count,
        failed_count=failed_count,
        message=f"Synced {synced_count} attempts. {failed_count} failed."
    )


@router.post("/pull", response_model=SyncPullResponse)
def sync_pull_questions(
    pull_request: SyncPullRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Pull new questions with DELTA SYNC optimization.
    
    Delta Sync Reduces Data Usage:
    - WITHOUT delta: Downloads all 200 questions every time (~2MB)
    - WITH delta: Only downloads changed questions since last sync (~50KB avg)
    
    Algorithm with Spaced Repetition:
    1. If last_sync_timestamp provided, filter by updated_at > timestamp
    2. Get questions due for SRS review (next_review_date <= now)
    3. Prioritize: 40% due reviews, 30% weak topics, 30% new material
    4. Return only changed questions (massive data savings)
    """
    # Get questions due for spaced repetition review
    due_question_ids = _get_due_review_questions(db, current_user.id)
    
    # Get user's performance by topic
    weak_topics = _calculate_weak_topics(db, current_user.id)
    
    # Build base query for questions (exclude soft-deleted)
    query = db.query(Question).filter(Question.deleted_at.is_(None))
    
    # DELTA SYNC: Filter by timestamp if provided
    if pull_request.last_sync_timestamp:
        query = query.filter(Question.updated_at > pull_request.last_sync_timestamp)
        print(f"🔄 Delta sync: fetching questions updated after {pull_request.last_sync_timestamp}")
    else:
        print("📦 Full sync: fetching all questions")
    
    # Filter by requested subjects
    if pull_request.subjects:
        query = query.filter(Question.subject.in_(pull_request.subjects))
    
    # Smart Question Selection with SRS Priority
    if due_question_ids and not pull_request.last_sync_timestamp:
        # PRIORITY 1: Spaced repetition reviews (40%)
        review_count = min(int(pull_request.limit * 0.4), len(due_question_ids))
        review_questions = query.filter(Question.id.in_(due_question_ids[:review_count])).all()
        
        # PRIORITY 2: Weak topics (30%)
        remaining = pull_request.limit - len(review_questions)
        if weak_topics and remaining > 0:
            weak_count = int(remaining * 0.5)  # 50% of remaining
            weak_questions = query.filter(
                Question.topic.in_(weak_topics),
                ~Question.id.in_(due_question_ids)  # Don't duplicate
            ).order_by(func.random()).limit(weak_count).all()
        else:
            weak_questions = []
        
        # PRIORITY 3: New/diverse material (30%)
        new_count = pull_request.limit - len(review_questions) - len(weak_questions)
        new_questions = query.filter(
            ~Question.id.in_(due_question_ids + [q.id for q in weak_questions])
        ).order_by(func.random()).limit(new_count).all()
        
        questions = review_questions + weak_questions + new_questions
        print(f"📚 SRS: {len(review_questions)} reviews, {len(weak_questions)} weak, {len(new_questions)} new")
        
    elif weak_topics and not pull_request.last_sync_timestamp:
        # Smart algorithm: 70% weak topics, 30% variety (only for full sync)
        weak_count = int(pull_request.limit * 0.7)
        random_count = pull_request.limit - weak_count
        
        weak_questions = query.filter(
            Question.topic.in_(weak_topics)
        ).order_by(func.random()).limit(weak_count).all()
        
        random_questions = query.filter(
            ~Question.topic.in_(weak_topics)
        ).order_by(func.random()).limit(random_count).all()
        
        questions = weak_questions + random_questions
    else:
        # Delta sync OR no weak areas: return what's changed/random
        questions = query.order_by(Question.updated_at.desc()).limit(pull_request.limit).all()
    
    # Calculate overall stats
    stats = _calculate_user_stats(db, current_user.id)

    # Include any newly graded submissions since last sync (for notifications)
    new_grades = []
    try:
        from app.models.classroom import Submission
        if pull_request.last_sync_timestamp:
            graded_subs = db.query(Submission).filter(
                Submission.student_id == current_user.id,
                Submission.is_graded == 1,
                Submission.graded_at > pull_request.last_sync_timestamp
            ).all()
        else:
            # For full sync, only include recent grades (last 7 days)
            from datetime import timedelta
            cutoff = datetime.utcnow() - timedelta(days=7)
            graded_subs = db.query(Submission).filter(
                Submission.student_id == current_user.id,
                Submission.is_graded == 1,
                Submission.graded_at >= cutoff
            ).all()

        for s in graded_subs:
            new_grades.append({
                'submission_id': s.id,
                'assignment_id': s.assignment_id,
                'grade': s.grade,
                'feedback': s.feedback,
                'graded_at': s.graded_at
            })
    except Exception:
        new_grades = []

    return SyncPullResponse(
        questions=[QuestionResponse.from_orm(q) for q in questions],
        weak_topics=weak_topics,
        total_attempts=stats['total_attempts'],
        accuracy=stats['accuracy'],
        synced_at=datetime.utcnow(),
        new_grades=new_grades
    )


def _get_due_review_questions(db: Session, user_id: int) -> List[int]:
    """
    Get question IDs that are due for spaced repetition review.
    Returns questions where next_review_date <= now.
    """
    now = datetime.utcnow()
    
    # Get most recent attempt for each question
    subquery = db.query(
        Attempt.question_id,
        func.max(Attempt.attempted_at).label('last_attempt')
    ).filter(
        Attempt.user_id == user_id
    ).group_by(Attempt.question_id).subquery()
    
    # Get attempts that are due for review
    due_attempts = db.query(Attempt.question_id).join(
        subquery,
        and_(
            Attempt.question_id == subquery.c.question_id,
            Attempt.attempted_at == subquery.c.last_attempt
        )
    ).filter(
        Attempt.user_id == user_id,
        Attempt.next_review_date <= now
    ).all()
    
    return [q_id for (q_id,) in due_attempts]


def _calculate_weak_topics(db: Session, user_id: int, threshold: float = 0.5) -> List[str]:
    """
    Find topics where user has < 50% accuracy.
    Returns list of topic names to focus on.
    """
    # Query: Group by topic, calculate accuracy
    results = db.query(
        Question.topic,
        func.count(Attempt.id).label('total'),
        func.sum(func.cast(Attempt.is_correct, Integer)).label('correct')
    ).join(
        Attempt, Attempt.question_id == Question.id
    ).filter(
        Attempt.user_id == user_id
    ).group_by(
        Question.topic
    ).having(
        func.count(Attempt.id) >= 5  # Need at least 5 attempts to judge
    ).all()
    
    weak_topics = []
    for topic, total, correct in results:
        accuracy = (correct or 0) / total if total > 0 else 0
        if accuracy < threshold:
            weak_topics.append(topic)
    
    return weak_topics


def _calculate_user_stats(db: Session, user_id: int) -> Dict:
    """Calculate overall user statistics."""
    total = db.query(func.count(Attempt.id)).filter(Attempt.user_id == user_id).scalar() or 0
    correct = db.query(func.sum(func.cast(Attempt.is_correct, Integer))).filter(
        Attempt.user_id == user_id
    ).scalar() or 0
    
    accuracy = (correct / total * 100) if total > 0 else 0
    
    return {
        'total_attempts': total,
        'correct_attempts': correct,
        'accuracy': round(accuracy, 2)
    }


@router.get("/stats")
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive user statistics.
    Used by mobile app dashboard.
    """
    stats = _calculate_user_stats(db, current_user.id)
    weak_topics = _calculate_weak_topics(db, current_user.id)
    
    # Get subject breakdown
    subject_stats = db.query(
        Question.subject,
        func.count(Attempt.id).label('total'),
        func.sum(func.cast(Attempt.is_correct, Integer)).label('correct')
    ).join(
        Attempt, Attempt.question_id == Question.id
    ).filter(
        Attempt.user_id == current_user.id
    ).group_by(
        Question.subject
    ).all()
    
    subjects_breakdown = {}
    for subject, total, correct in subject_stats:
        accuracy = (correct or 0) / total * 100 if total > 0 else 0
        subjects_breakdown[subject.value] = {
            'attempts': total,
            'correct': correct or 0,
            'accuracy': round(accuracy, 2)
        }
    
    # Calculate streak (days with at least 1 attempt)
    streak_days = _calculate_streak(db, current_user.id)
    
    return {
        **stats,
        'weak_topics': weak_topics,
        'subjects_breakdown': subjects_breakdown,
        'streak_days': streak_days
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
    ).limit(365).all()  # Check last year max
    
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


@router.get("/reviews/due")
def get_due_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get questions due for spaced repetition review.
    
    Mobile app can show: "📚 5 reviews due today!"
    """
    due_question_ids = _get_due_review_questions(db, current_user.id)
    
    # Get question details
    questions = db.query(Question).filter(Question.id.in_(due_question_ids)).all()
    
    return {
        "due_count": len(due_question_ids),
        "questions": [QuestionResponse.from_orm(q) for q in questions],
        "message": f"You have {len(due_question_ids)} reviews due today! 📚"
    }
