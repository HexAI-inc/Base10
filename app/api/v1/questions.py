"""Questions API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List, Optional
import json
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.models.question import Question
from app.models.enums import Subject, DifficultyLevel, Topic
from app.models.progress import Attempt
from app.schemas.schemas import QuestionResponse, AttemptCreate, AttemptResponse
from app.api.v1.auth import get_current_user
from app.core.spaced_repetition import calculate_next_review_sm2, quality_from_attempt

router = APIRouter()


@router.get("/", response_model=List[QuestionResponse])
def get_questions(
    subject: Optional[Subject] = None,
    topic: Optional[Topic] = None,
    difficulty: Optional[DifficultyLevel] = None,
    limit: int = Query(default=50, le=200),
    skip: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get questions with filtering.
    
    Optimized for offline sync:
    - Max 200 questions per request (mobile storage constraints)
    - Filters by subject/topic/difficulty
    - Pagination support
    """
    query = db.query(Question)
    
    # Apply filters
    if subject:
        query = query.filter(Question.subject == subject)
    if topic:
        query = query.filter(Question.topic == topic)
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)
    
    # Get paginated results
    questions = query.offset(skip).limit(limit).all()
    
    return questions


@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get single question by ID."""
    question = db.query(Question).filter(Question.id == question_id).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return question


@router.get("/subjects/list")
def get_subjects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get list of all subjects with question counts.
    Useful for mobile app to show available content.
    """
    subjects = db.query(
        Question.subject, 
        func.count(Question.id)
    ).group_by(Question.subject).all()
    
    return [{"subject": s[0].value, "count": s[1]} for s in subjects]


@router.get("/topics/{subject}")
def get_topics(
    subject: Subject,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all topics for a subject.
    Helps mobile app show topic selection menu.
    """
    topics = db.query(Question.topic, db.func.count(Question.id)).filter(
        Question.subject == subject
    ).group_by(Question.topic).all()
    
    return [{"topic": t[0], "count": t[1]} for t in topics]


@router.get("/practice/{subject}/{topic}")
def get_topic_practice_questions(
    subject: Subject,
    topic: str,
    count: int = Query(default=10, le=50),
    difficulty: Optional[DifficultyLevel] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get practice questions for a specific subject and topic.
    
    Optimized for focused topic practice sessions.
    Questions are ordered by difficulty (easy to hard) for progressive learning.
    """
    query = db.query(Question).filter(
        Question.subject == subject,
        Question.topic == topic
    )
    
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)
    
    # Order by difficulty for progressive learning
    difficulty_order = case(
        (Question.difficulty == DifficultyLevel.EASY, 1),
        (Question.difficulty == DifficultyLevel.MEDIUM, 2),
        (Question.difficulty == DifficultyLevel.HARD, 3),
        else_=4
    )
    
    questions = query.order_by(difficulty_order).limit(count).all()
    
    if not questions:
        raise HTTPException(
            status_code=404,
            detail=f"No questions found for {subject.value} - {topic}"
        )
    
    return questions


@router.get("/practice/{subject}")
def get_subject_practice_questions(
    subject: Subject,
    count: int = Query(default=20, le=100),
    difficulty: Optional[DifficultyLevel] = None,
    exclude_topics: Optional[List[str]] = Query(None, description="Topics to exclude"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get practice questions for a subject with optional topic filtering.
    
    Useful for general subject practice or excluding certain topics.
    """
    query = db.query(Question).filter(Question.subject == subject)
    
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)
    
    if exclude_topics:
        query = query.filter(~Question.topic.in_(exclude_topics))
    
    questions = query.order_by(func.random()).limit(count).all()
    
    if not questions:
        raise HTTPException(
            status_code=404,
            detail=f"No questions found for {subject.value}"
        )
    
    return questions


@router.get("/{question_id}/explain")
async def get_question_explanation(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-powered explanation for any question.
    
    Unlike /ai/explain which requires a wrong answer, this provides
    explanations for learning purposes regardless of performance.
    """
    # Fetch the question
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check AI quota
    from app.services.ai_service import check_ai_quota, increment_ai_usage
    if not check_ai_quota(db, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="AI quota exceeded. Please wait for reset or upgrade."
        )
    
    # Generate comprehensive explanation
    try:
        from app.services.ai_service import generate_comprehensive_explanation
        explanation = await generate_comprehensive_explanation(question)
    except ImportError:
        # Fallback to stored explanation
        explanation = question.explanation or "No explanation available for this question."
    except Exception as e:
        explanation = question.explanation or f"Explanation service temporarily unavailable: {str(e)}"
    
    # Increment usage
    increment_ai_usage(db, current_user.id, "explanation")
    
    return {
        "question_id": question_id,
        "explanation": explanation,
        "topic": question.topic,
        "subject": question.subject.value,
        "difficulty": question.difficulty.value
    }


@router.get("/weak-topics/{subject}")
def get_weak_topics_practice(
    subject: Subject,
    count: int = Query(default=15, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get questions from topics where the student needs the most practice.
    
    Analyzes student's performance and prioritizes weak areas.
    """
    # Get student's performance by topic
    from sqlalchemy import and_, case
    
    topic_performance = db.query(
        Question.topic,
        func.count(Attempt.id).label('total_attempts'),
        func.sum(case((Attempt.is_correct == True, 1), else_=0)).label('correct_attempts')
    ).join(
        Question, Attempt.question_id == Question.id
    ).filter(
        and_(
            Attempt.user_id == current_user.id,
            Question.subject == subject
        )
    ).group_by(Question.topic).all()
    
    # Calculate accuracy and identify weak topics (accuracy < 70%)
    weak_topics = []
    for topic, total, correct in topic_performance:
        if total >= 3:  # Only consider topics with at least 3 attempts
            accuracy = (correct / total) * 100
            if accuracy < 70:
                weak_topics.append((topic, accuracy, total))
    
    # Sort by accuracy (worst first)
    weak_topics.sort(key=lambda x: x[1])
    
    if not weak_topics:
        # If no weak topics, return general practice questions
        return get_subject_practice_questions(subject, count, None, None, db, current_user)
    
    # Get questions from weak topics (distribute across topics)
    questions_per_topic = max(1, count // len(weak_topics))
    all_questions = []
    
    for topic, _, _ in weak_topics:
        topic_questions = db.query(Question).filter(
            and_(
                Question.subject == subject,
                Question.topic == topic
            )
        ).order_by(func.random()).limit(questions_per_topic).all()
        all_questions.extend(topic_questions)
    
    # If we don't have enough, fill with random questions
    if len(all_questions) < count:
        remaining = count - len(all_questions)
        extra_questions = db.query(Question).filter(
            Question.subject == subject
        ).order_by(func.random()).limit(remaining).all()
        all_questions.extend(extra_questions)
    
    return all_questions[:count]  # Ensure we don't exceed requested count


# TEMPORARY DEVELOPMENT ENDPOINTS - Remove after frontend auth is fixed

@router.get("/practice/{subject}/{topic}/public")
def get_topic_practice_questions_public(
    subject: Subject,
    topic: str,
    count: int = Query(default=5, le=20),
    difficulty: Optional[DifficultyLevel] = None,
    db: Session = Depends(get_db)
):
    """
    TEMPORARY: Get topic practice questions without authentication for development.
    REMOVE THIS ENDPOINT AFTER FRONTEND AUTH IS IMPLEMENTED.
    """
    query = db.query(Question).filter(
        Question.subject == subject,
        Question.topic == topic
    )
    
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)
    
    # Order by difficulty for progressive learning
    difficulty_order = case(
        (Question.difficulty == DifficultyLevel.EASY, 1),
        (Question.difficulty == DifficultyLevel.MEDIUM, 2),
        (Question.difficulty == DifficultyLevel.HARD, 3),
        else_=4
    )
    
    questions = query.order_by(difficulty_order).limit(count).all()
    
    if not questions:
        raise HTTPException(
            status_code=404,
            detail=f"No questions found for {subject.value} - {topic}"
        )
    
    return questions


@router.get("/topics/{subject}/public")
def get_topics_public(
    subject: Subject,
    db: Session = Depends(get_db)
):
    """
    TEMPORARY: Get topics for a subject without authentication for development.
    REMOVE THIS ENDPOINT AFTER FRONTEND AUTH IS IMPLEMENTED.
    """
    topics = db.query(Question.topic, func.count(Question.id)).filter(
        Question.subject == subject
    ).group_by(Question.topic).all()
    
    return [{"topic": t[0], "count": t[1]} for t in topics]


@router.post("/submit", response_model=AttemptResponse)
def submit_answer(
    attempt_data: AttemptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit an answer for a question.
    
    Processes the attempt immediately, calculates spaced repetition schedule,
    and returns the created attempt record.
    """
    # Verify question exists
    question = db.query(Question).filter(Question.id == attempt_data.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Calculate SM-2 spaced repetition schedule
    quality = quality_from_attempt(attempt_data.is_correct)
    
    # Get previous attempt for this question to continue SRS chain
    previous_attempt = db.query(Attempt).filter(
        Attempt.user_id == current_user.id,
        Attempt.question_id == attempt_data.question_id
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
        device_id=attempt_data.device_id,
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
    db.commit()
    db.refresh(new_attempt)
    
    return new_attempt
