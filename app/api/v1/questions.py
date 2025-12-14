"""Questions API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.db.session import get_db
from app.models.user import User
from app.models.question import Question, Subject, DifficultyLevel
from app.schemas.schemas import QuestionResponse, SubjectEnum, DifficultyEnum
from app.api.v1.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[QuestionResponse])
def get_questions(
    subject: Optional[SubjectEnum] = None,
    topic: Optional[str] = None,
    difficulty: Optional[DifficultyEnum] = None,
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
        query = query.filter(Question.topic.ilike(f"%{topic}%"))
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
        db.func.count(Question.id)
    ).group_by(Question.subject).all()
    
    return [{"subject": s[0].value, "count": s[1]} for s in subjects]


@router.get("/topics/{subject}")
def get_topics(
    subject: SubjectEnum,
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


@router.get("/random/{subject}")
def get_random_questions(
    subject: SubjectEnum,
    count: int = Query(default=10, le=50),
    difficulty: Optional[DifficultyEnum] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get random questions for quick practice.
    Used by SMS bot and mobile quick quiz.
    """
    query = db.query(Question).filter(Question.subject == subject)
    
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)
    
    questions = query.order_by(db.func.random()).limit(count).all()
    
    return questions
