"""Base classroom CRUD endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.db.session import get_db
from app.models.classroom import Classroom, classroom_students
from app.models.user import User
from app.models.enums import UserRole
from app.models.progress import Attempt
from app.models.question import Question
from app.core.security import get_current_user
from app.schemas.schemas import (
    ClassroomCreate, 
    ClassroomResponse, 
    ClassroomUpdate,
    ClassroomAnalytics,
    TopicPerformance,
    StudentPerformance
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ClassroomResponse)
async def create_classroom(classroom_data: ClassroomCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Create a new classroom.
    
    Only teachers and admins can create classrooms.
    """
    # Enforce role-based access
    if user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only teachers can create classrooms. Please update your account role to 'teacher'."
        )
    
    join_code = Classroom.generate_join_code()
    classroom = Classroom(
        teacher_id=user.id,
        name=classroom_data.name,
        description=classroom_data.description,
        subject=classroom_data.subject,
        grade_level=classroom_data.grade_level,
        join_code=join_code
    )
    db.add(classroom)
    db.commit()
    db.refresh(classroom)
    
    logger.info(f"👩‍🏫 Teacher {user.id} ({user.full_name or user.username}) created classroom: {classroom.name}")
    
    # Add student count for response model
    classroom.student_count = 0
    
    return classroom


@router.get("", response_model=List[dict])
async def list_classrooms(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """List classrooms. Teachers see their own, students see enrolled classrooms."""
    
    # Get classrooms where user is the teacher
    teacher_classrooms = db.query(
        Classroom,
        func.count(classroom_students.c.student_id).label('student_count')
    ).outerjoin(
        classroom_students,
        Classroom.id == classroom_students.c.classroom_id
    ).filter(
        Classroom.teacher_id == user.id,
        Classroom.is_active == True
    ).group_by(
        Classroom.id
    ).all()
    
    # Get classrooms where user is a student
    student_classrooms = db.query(
        Classroom,
        func.count(classroom_students.c.student_id).label('student_count')
    ).join(
        classroom_students,
        Classroom.id == classroom_students.c.classroom_id
    ).filter(
        classroom_students.c.student_id == user.id,
        Classroom.is_active == True
    ).group_by(
        Classroom.id
    ).all()
    
    result = []
    
    # Add teacher classrooms
    for classroom, count in teacher_classrooms:
        result.append({
            "id": classroom.id,
            "name": classroom.name,
            "description": classroom.description,
            "subject": classroom.subject,
            "grade_level": classroom.grade_level,
            "join_code": classroom.join_code,
            "student_count": count,
            "role": "teacher",
            "created_at": classroom.created_at
        })
        
    # Add student classrooms
    for classroom, count in student_classrooms:
        result.append({
            "id": classroom.id,
            "name": classroom.name,
            "description": classroom.description,
            "subject": classroom.subject,
            "grade_level": classroom.grade_level,
            "student_count": count,
            "role": "student",
            "created_at": classroom.created_at
        })
        
    return result


@router.get("/{classroom_id}", response_model=ClassroomResponse)
async def get_classroom(classroom_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get classroom details."""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    # Check if user is teacher or student in this classroom
    is_student = db.query(classroom_students).filter(
        classroom_students.c.classroom_id == classroom_id,
        classroom_students.c.student_id == user.id
    ).first()
    
    if classroom.teacher_id != user.id and not is_student and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not a member of this classroom")
    
    # Get student count
    student_count = db.query(func.count(classroom_students.c.student_id)).filter(
        classroom_students.c.classroom_id == classroom_id
    ).scalar()
    
    classroom.student_count = student_count
    return classroom


@router.patch("/{classroom_id}", response_model=ClassroomResponse)
async def update_classroom(
    classroom_id: int, 
    classroom_data: ClassroomUpdate, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    """Update classroom details (Teacher only)."""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    if classroom.teacher_id != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only the teacher can update classroom details")
    
    update_data = classroom_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(classroom, key, value)
    
    db.commit()
    db.refresh(classroom)
    
    # Get student count
    student_count = db.query(func.count(classroom_students.c.student_id)).filter(
        classroom_students.c.classroom_id == classroom_id
    ).scalar()
    classroom.student_count = student_count
    
    return classroom


@router.get("/{classroom_id}/analytics", response_model=ClassroomAnalytics)
async def get_classroom_analytics(
    classroom_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive analytics for a classroom.
    
    This is THE CORE FEATURE for teachers:
    - See which students are struggling
    - Identify misconceptions (high confidence + wrong answers)
    - Detect guessing patterns
    - Find weak topics needing review
    
    Powered by psychometric data from attempts.
    """
    # Verify teacher owns this classroom
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found"
        )
    
    if classroom.teacher_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this classroom's analytics"
        )
    
    # Get student IDs in this classroom
    student_ids = [row[0] for row in db.query(classroom_students.c.student_id).filter(classroom_students.c.classroom_id == classroom_id).all()]
    
    if not student_ids:
        return ClassroomAnalytics(
            classroom_id=classroom_id,
            classroom_name=classroom.name,
            total_students=0,
            active_students=0,
            total_attempts=0,
            average_accuracy=0.0,
            avg_time_per_question_ms=None,
            guessing_rate=0.0,
            struggle_rate=0.0,
            students=[],
            topics=[]
        )
    
    # Calculate per-student performance
    students_performance = []
    for student_id in student_ids:
        user = db.query(User).filter(User.id == student_id).first()
        
        attempts = db.query(Attempt).filter(Attempt.user_id == student_id).all()
        
        if not attempts:
            students_performance.append(StudentPerformance(
                user_id=student_id,
                full_name=user.full_name or "Unknown",
                total_attempts=0,
                correct_attempts=0,
                accuracy=0.0,
                avg_time_ms=None,
                guessing_rate=0.0,
                struggle_rate=0.0,
                misconception_count=0
            ))
            continue
        
        total = len(attempts)
        correct = sum(1 for a in attempts if a.is_correct)
        accuracy = (correct / total * 100) if total > 0 else 0
        
        # Psychometric analysis
        times = [a.time_taken_ms for a in attempts if a.time_taken_ms]
        avg_time = sum(times) / len(times) if times else None
        
        # Guessing: < 2000ms
        guesses = sum(1 for a in attempts if a.time_taken_ms and a.time_taken_ms < 2000)
        guessing_rate = (guesses / total * 100) if total > 0 else 0
        
        # Struggling: > 60000ms
        struggles = sum(1 for a in attempts if a.time_taken_ms and a.time_taken_ms > 60000)
        struggle_rate = (struggles / total * 100) if total > 0 else 0
        
        # Misconceptions: confidence >= 4 BUT wrong
        misconceptions = sum(
            1 for a in attempts 
            if a.confidence_level and a.confidence_level >= 4 and not a.is_correct
        )
        
        students_performance.append(StudentPerformance(
            user_id=student_id,
            full_name=user.full_name or "Unknown",
            total_attempts=total,
            correct_attempts=correct,
            accuracy=round(accuracy, 2),
            avg_time_ms=round(avg_time, 2) if avg_time else None,
            guessing_rate=round(guessing_rate, 2),
            struggle_rate=round(struggle_rate, 2),
            misconception_count=misconceptions
        ))
    
    # Calculate topic performance
    topic_stats = db.query(
        Question.topic,
        func.count(Attempt.id).label('total'),
        func.avg(case((Attempt.is_correct, 1), else_=0)).label('accuracy'),
        func.avg(Attempt.confidence_level).label('avg_confidence')
    ).join(
        Attempt, Attempt.question_id == Question.id
    ).filter(
        Attempt.user_id.in_(student_ids)
    ).group_by(
        Question.topic
    ).all()
    
    topics = []
    for topic, total, accuracy, avg_conf in topic_stats:
        # Count students struggling with this topic (< 50% accuracy)
        struggling = db.query(Attempt.user_id).filter(
            Attempt.user_id.in_(student_ids),
            Attempt.question_id.in_(
                db.query(Question.id).filter(Question.topic == topic)
            )
        ).group_by(Attempt.user_id).having(
            func.avg(case((Attempt.is_correct, 1), else_=0)) < 0.5
        ).count()
        
        topics.append(TopicPerformance(
            topic=topic,
            total_attempts=total,
            accuracy=round(accuracy * 100, 2),
            avg_confidence=round(avg_conf, 2) if avg_conf else None,
            struggling_students=struggling
        ))
    
    # Get all attempts for these students
    student_attempts = db.query(Attempt).filter(Attempt.user_id.in_(student_ids)).all()
    
    total_attempts = len(student_attempts)
    correct_attempts = sum(1 for a in student_attempts if a.is_correct)
    avg_accuracy = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
    
    # Average confidence
    confidences = [a.confidence_level for a in student_attempts if a.confidence_level is not None]
    avg_confidence = sum(confidences) / len(confidences) if confidences else None
    
    # Active students (attempts in last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    active_students = db.query(func.count(func.distinct(Attempt.user_id))).filter(
        Attempt.user_id.in_(student_ids),
        Attempt.attempted_at >= week_ago
    ).scalar() or 0
    
    # Psychometric class averages
    all_times = [a.time_taken_ms for a in student_attempts if a.time_taken_ms]
    avg_time_class = sum(all_times) / len(all_times) if all_times else None
    
    guesses_class = sum(1 for a in student_attempts if a.time_taken_ms and a.time_taken_ms < 2000)
    guessing_rate_class = (guesses_class / total_attempts * 100) if total_attempts > 0 else 0
    
    struggles_class = sum(1 for a in student_attempts if a.time_taken_ms and a.time_taken_ms > 60000)
    struggle_rate_class = (struggles_class / total_attempts * 100) if total_attempts > 0 else 0
    
    return ClassroomAnalytics(
        classroom_id=classroom_id,
        classroom_name=classroom.name,
        total_students=len(student_ids),
        active_students=active_students,
        total_attempts=total_attempts,
        average_accuracy=round(avg_accuracy, 2),
        average_confidence=round(avg_confidence, 2) if avg_confidence else None,
        avg_time_per_question_ms=round(avg_time_class, 2) if avg_time_class else None,
        guessing_rate=round(guessing_rate_class, 2),
        struggle_rate=round(struggle_rate_class, 2),
        students=students_performance,
        topics=topics
    )
