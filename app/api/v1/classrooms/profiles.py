"""Classroom student profiles and messaging endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, Integer
from typing import Optional, List
from datetime import datetime
import logging
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models.classroom import Classroom, Assignment, Submission, classroom_students
from app.models.user import User
from app.models.enums import UserRole
from app.models.student_profile import StudentProfile, TeacherMessage
from app.models.progress import Attempt
from app.core.security import get_current_user
from app.services.comms_service import CommunicationService, MessageType, MessagePriority

logger = logging.getLogger(__name__)

router = APIRouter()


class StudentProfileUpdate(BaseModel):
    notes: Optional[str] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    learning_style: Optional[str] = None
    participation_level: Optional[str] = None
    homework_completion_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    ai_context: Optional[str] = None
    contact_frequency: Optional[str] = None


class SendMessageRequest(BaseModel):
    subject: Optional[str] = None
    message: str = Field(..., min_length=1)
    message_type: str = Field(default="general")


class AIContextRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)


@router.get("/{classroom_id}/students/{student_id}/profile")
async def get_student_profile(
    classroom_id: int, 
    student_id: int, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    """Get comprehensive student profile for a specific classroom."""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    if classroom.teacher_id != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only the classroom teacher can view student profiles")
    
    # Verify student is in classroom
    is_enrolled = db.query(classroom_students).filter(
        classroom_students.c.classroom_id == classroom_id,
        classroom_students.c.student_id == student_id
    ).first()
    
    if not is_enrolled:
        raise HTTPException(status_code=404, detail="Student not enrolled in this classroom")
    
    # Get student info
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get or create student profile
    profile = db.query(StudentProfile).filter(
        StudentProfile.classroom_id == classroom_id,
        StudentProfile.student_id == student_id
    ).first()
    
    # Assignment performance
    total_assignments = db.query(func.count(Assignment.id)).filter(
        Assignment.classroom_id == classroom_id,
        Assignment.status == "published"
    ).scalar() or 0
    
    submissions = db.query(Submission).filter(
        Submission.student_id == student_id
    ).join(Assignment).filter(
        Assignment.classroom_id == classroom_id
    ).all()
    
    submitted_count = len(submissions)
    graded_submissions = [s for s in submissions if s.is_graded]
    
    avg_grade = None
    if graded_submissions:
        total_score = sum([s.grade or 0 for s in graded_submissions])
        total_possible = sum([db.query(Assignment).filter(Assignment.id == s.assignment_id).first().max_points or 100 for s in graded_submissions])
        avg_grade = (total_score / total_possible * 100) if total_possible > 0 else 0
    
    # Quiz activity
    from app.models.question import Question
    total_attempts = db.query(func.count(Attempt.id)).filter(
        Attempt.user_id == student_id
    ).scalar() or 0
    
    correct_attempts = db.query(func.count(Attempt.id)).filter(
        Attempt.user_id == student_id,
        Attempt.is_correct == True
    ).scalar() or 0
    
    overall_accuracy = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
    
    # Topic breakdown
    topic_stats = db.query(
        Question.topic,
        func.count(Attempt.id).label('attempts'),
        func.sum(func.cast(Attempt.is_correct, Integer)).label('correct')
    ).join(
        Attempt, Question.id == Attempt.question_id
    ).filter(
        Attempt.user_id == student_id
    ).group_by(Question.topic).all()
    
    topics = []
    for topic, attempts, correct in topic_stats:
        accuracy = (correct / attempts * 100) if attempts > 0 else 0
        topics.append({
            "topic": topic,
            "attempts": attempts,
            "accuracy": round(accuracy, 1)
        })
    
    # Recent activity
    recent_submissions = db.query(Submission).filter(
        Submission.student_id == student_id
    ).join(Assignment).filter(
        Assignment.classroom_id == classroom_id
    ).order_by(Submission.submitted_at.desc()).limit(5).all()
    
    recent_activity = []
    for sub in recent_submissions:
        assignment = db.query(Assignment).filter(Assignment.id == sub.assignment_id).first()
        recent_activity.append({
            "type": "submission",
            "assignment_title": assignment.title if assignment else "Unknown",
            "submitted_at": sub.submitted_at.isoformat(),
            "is_graded": sub.is_graded,
            "grade": sub.grade
        })
    
    return {
        "student": {
            "id": student.id,
            "full_name": student.full_name or student.username,
            "username": student.username,
            "email": student.email,
            "avatar_url": student.avatar_url,
            "joined_at": is_enrolled.joined_at.isoformat() if is_enrolled else None
        },
        "classroom_performance": {
            "total_assignments": total_assignments,
            "submitted": submitted_count,
            "graded": len(graded_submissions),
            "submission_rate": round(submitted_count / total_assignments * 100, 1) if total_assignments > 0 else 0,
            "average_grade": round(avg_grade, 1) if avg_grade is not None else None
        },
        "quiz_activity": {
            "total_attempts": total_attempts,
            "correct": correct_attempts,
            "overall_accuracy": round(overall_accuracy, 1),
            "topics": topics[:10]
        },
        "teacher_notes": {
            "notes": profile.notes if profile else None,
            "strengths": profile.strengths if profile else None,
            "weaknesses": profile.weaknesses if profile else None,
            "learning_style": profile.learning_style if profile else None,
            "participation_level": profile.participation_level if profile else None,
            "homework_completion_rate": profile.homework_completion_rate if profile else None,
            "ai_context": profile.ai_context if profile else None,
            "last_contacted": profile.last_contacted.isoformat() if profile and profile.last_contacted else None
        },
        "recent_activity": recent_activity
    }


@router.put("/{classroom_id}/students/{student_id}/profile")
async def update_student_profile(
    classroom_id: int,
    student_id: int,
    profile_data: StudentProfileUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Update teacher's notes and observations about a student."""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    if classroom.teacher_id != user.id:
        raise HTTPException(status_code=403, detail="Only the classroom teacher can update student profiles")
    
    # Get or create profile
    profile = db.query(StudentProfile).filter(
        StudentProfile.classroom_id == classroom_id,
        StudentProfile.student_id == student_id
    ).first()
    
    if not profile:
        profile = StudentProfile(
            classroom_id=classroom_id,
            student_id=student_id,
            teacher_id=user.id
        )
        db.add(profile)
    
    # Update fields
    update_dict = profile_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    
    return {"message": "Profile updated successfully"}


@router.post("/{classroom_id}/students/{student_id}/message")
async def send_student_message(
    classroom_id: int,
    student_id: int,
    message_data: SendMessageRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Send a personalized message from teacher to student."""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    if classroom.teacher_id != user.id:
        raise HTTPException(status_code=403, detail="Only the classroom teacher can send messages")
    
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Create message
    teacher_message = TeacherMessage(
        classroom_id=classroom_id,
        teacher_id=user.id,
        student_id=student_id,
        subject=message_data.subject,
        message=message_data.message,
        message_type=message_data.message_type
    )
    db.add(teacher_message)
    
    # Update last contacted
    profile = db.query(StudentProfile).filter(
        StudentProfile.classroom_id == classroom_id,
        StudentProfile.student_id == student_id
    ).first()
    
    if profile:
        profile.last_contacted = datetime.utcnow()
        db.add(profile)
    
    db.commit()
    
    # Send notification
    try:
        comms = CommunicationService()
        priority = MessagePriority.HIGH if message_data.message_type in ["concern", "urgent"] else MessagePriority.MEDIUM
        
        comms.send_notification(
            user_id=student_id,
            message_type=MessageType.ACHIEVEMENT_UNLOCKED,
            priority=priority,
            title=f"📬 Message from {user.full_name or user.username}",
            body=f"{classroom.name}: {message_data.subject or 'New message'}",
            data={
                "type": "teacher_message",
                "classroom_id": classroom_id,
                "teacher_name": user.full_name or user.username
            },
            user_phone=student.phone_number,
            user_email=student.email,
            has_app_installed=student.has_app_installed or False
        )
    except Exception as e:
        logger.error(f"❌ Failed to send message notification: {e}")

    return {"message": "Message sent successfully"}


@router.get("/{classroom_id}/students/{student_id}/messages")
async def get_student_messages(
    classroom_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get the message history a teacher has sent to a student in this classroom."""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    if classroom.teacher_id != user.id and user.id != student_id and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to view these messages")

    messages = db.query(TeacherMessage).filter(
        TeacherMessage.classroom_id == classroom_id,
        TeacherMessage.student_id == student_id
    ).order_by(TeacherMessage.sent_at.desc()).all()

    return [
        {
            "id": m.id,
            "subject": m.subject,
            "message": m.message,
            "message_type": m.message_type,
            "is_read": bool(m.is_read),
            "sent_at": m.sent_at.isoformat() if m.sent_at else None,
            "read_at": m.read_at.isoformat() if m.read_at else None,
        }
        for m in messages
    ]


@router.post("/{classroom_id}/students/{student_id}/ai-context")
async def get_student_ai_context(
    classroom_id: int,
    student_id: int,
    payload: AIContextRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Ask the AI teaching assistant a question about a specific student, using
    the teacher's notes (StudentProfile.ai_context) as grounding context."""
    from app.services import ai_service

    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    if classroom.teacher_id != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only the classroom teacher can use this")

    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if not ai_service.GEMINI_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI assistant is currently unavailable")

    profile = db.query(StudentProfile).filter(
        StudentProfile.classroom_id == classroom_id,
        StudentProfile.student_id == student_id
    ).first()

    context_parts = [f"Student: {student.full_name or student.username}, classroom: {classroom.name}."]
    if profile:
        if profile.notes:
            context_parts.append(f"Teacher notes: {profile.notes}")
        if profile.strengths:
            context_parts.append(f"Strengths: {profile.strengths}")
        if profile.weaknesses:
            context_parts.append(f"Weaknesses: {profile.weaknesses}")
        if profile.learning_style:
            context_parts.append(f"Learning style: {profile.learning_style}")
        if profile.ai_context:
            context_parts.append(f"Additional context: {profile.ai_context}")

    prompt = (
        "\n".join(context_parts)
        + f"\n\nTeacher's question about this student: {payload.question}"
        + "\n\nProvide a concise, actionable answer for the teacher:"
    )

    try:
        response = ai_service.model.generate_content(prompt)
        return {
            "answer": response.text,
            "student_id": student_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Student AI context error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate response")
