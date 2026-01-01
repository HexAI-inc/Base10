"""Classroom AI integration endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import logging
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models.classroom import Classroom, Assignment
from app.models.user import User
from app.models.question import Question
from app.models.enums import UserRole, AssignmentType, AssignmentStatus
from app.core.security import get_current_user
from app.schemas.schemas import (
    TeacherAIRequest, 
    TeacherAIResponse, 
    ApproveQuizRequest,
    AssignmentResponse
)
from app.services.teacher_ai_assistant import process_teacher_command

logger = logging.getLogger(__name__)

router = APIRouter()


class AskAIRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    context: Optional[str] = None


@router.post("/{classroom_id}/ask-ai")
async def ask_ai_teacher(classroom_id: int, payload: AskAIRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Ask AI teacher a question in classroom context.
    """
    from app.services import ai_service
    
    # Verify user has access to classroom
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    # Check if user is teacher or student in this classroom
    from app.models.classroom import classroom_students
    is_student = db.query(classroom_students).filter(
        classroom_students.c.classroom_id == classroom_id,
        classroom_students.c.student_id == user.id
    ).first()
    
    is_teacher = classroom.teacher_id == user.id
    
    if not (is_teacher or is_student):
        raise HTTPException(status_code=403, detail="Not a member of this classroom")
    
    if not ai_service.GEMINI_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI teacher is currently unavailable")
    
    # Build context-aware prompt
    classroom_context = f"""
You are an AI teaching assistant for {classroom.name}.
Subject: {classroom.subject or 'General'}
Grade Level: {classroom.grade_level or 'Not specified'}

Your role:
- Answer student questions clearly and pedagogically
- Relate answers to the classroom subject and level
- Encourage critical thinking
- Use examples appropriate for the grade level
"""
    
    # Get recent assignments for additional context
    recent_assignments = db.query(Assignment).filter(
        Assignment.classroom_id == classroom_id,
        Assignment.status == "published"
    ).order_by(Assignment.created_at.desc()).limit(3).all()
    
    if recent_assignments:
        assignment_topics = [a.title for a in recent_assignments]
        classroom_context += f"\n\nRecent topics covered: {', '.join(assignment_topics)}"
    
    if payload.context:
        classroom_context += f"\n\nAdditional context: {payload.context}"
    
    # Generate AI response
    try:
        full_prompt = f"{classroom_context}\n\nStudent Question: {payload.question}\n\nProvide a helpful, educational response:"
        response = ai_service.model.generate_content(full_prompt)
        
        logger.info(f"🤖 AI teacher answered question in classroom {classroom_id} for user {user.id}")
        
        return {
            "answer": response.text,
            "classroom_name": classroom.name,
            "subject": classroom.subject,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ AI teacher error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate response")


@router.post("/teacher-assistant", response_model=TeacherAIResponse)
async def teacher_ai_assistant(
    request: TeacherAIRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI Assistant for teachers - natural language classroom management.
    """
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can use the AI assistant"
        )
    
    # Prepare context
    context = request.context or {}
    if request.classroom_id:
        context['classroom_id'] = request.classroom_id
    
    # Process request
    result = await process_teacher_command(
        db=db,
        teacher=current_user,
        message=request.message,
        context=context
    )
    
    return result


@router.post("/approve-quiz", response_model=AssignmentResponse)
async def approve_and_send_quiz(
    request: ApproveQuizRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve AI-generated quiz and send to students.
    """
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can approve quizzes"
        )
    
    # Verify classroom ownership
    classroom = db.query(Classroom).filter(
        Classroom.id == request.classroom_id,
        Classroom.teacher_id == current_user.id
    ).first()
    
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found or you don't have permission"
        )
    
    # Verify all questions exist
    questions = db.query(Question).filter(
        Question.id.in_(request.question_ids)
    ).all()
    
    if len(questions) != len(request.question_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some questions were not found"
        )
    
    # Determine filters from questions (for consistency)
    subjects = set(q.subject for q in questions if q.subject)
    topics = set(q.topic for q in questions if q.topic)
    difficulties = set(q.difficulty for q in questions if q.difficulty)
    
    # Create assignment
    assignment = Assignment(
        classroom_id=request.classroom_id,
        title=request.title,
        description=request.description,
        subject_filter=subjects.pop() if len(subjects) == 1 else None,
        topic_filter=topics.pop() if len(topics) == 1 else None,
        difficulty_filter=difficulties.pop() if len(difficulties) == 1 else None,
        question_count=len(request.question_ids),
        due_date=request.due_date,
        assignment_type=AssignmentType.QUIZ,
        status=AssignmentStatus.PUBLISHED,
        total_points=len(request.question_ids) * request.points_per_question
    )
    
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    return assignment
