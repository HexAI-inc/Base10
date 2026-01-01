"""Classroom AI integration endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import logging
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models.classroom import Classroom, Assignment
from app.models.user import User
from app.core.security import get_current_user

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
