"""Teacher API endpoints - Classroom management and student analytics."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models.user import User
from app.models.classroom import Classroom, Assignment, classroom_students
from app.models.progress import Attempt
from app.models.question import Question
from app.core.security import get_current_user

router = APIRouter()


# ============= Schemas =============

class ClassroomCreate(BaseModel):
    """Schema for creating a classroom."""
    name: str = Field(..., min_length=3, max_length=100, description="Classroom name")
    description: Optional[str] = Field(None, max_length=500)


class ClassroomResponse(BaseModel):
    """Schema for classroom responses."""
    id: int
    name: str
    description: Optional[str]
    join_code: str
    is_active: int
    student_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ClassroomJoin(BaseModel):
    """Schema for students joining a classroom."""
    join_code: str = Field(..., min_length=7, max_length=12)


class AssignmentCreate(BaseModel):
    """Schema for creating an assignment."""
    classroom_id: int
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    subject_filter: Optional[str] = None
    topic_filter: Optional[str] = None
    difficulty_filter: Optional[str] = None
    question_count: int = Field(default=10, ge=1, le=50)
    due_date: Optional[datetime] = None


class AssignmentResponse(BaseModel):
    """Schema for assignment responses."""
    id: int
    classroom_id: int
    title: str
    description: Optional[str]
    subject_filter: Optional[str]
    topic_filter: Optional[str]
    question_count: int
    due_date: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class StudentPerformance(BaseModel):
    """Individual student performance in a classroom."""
    user_id: int
    full_name: str
    total_attempts: int
    correct_attempts: int
    accuracy: float
    avg_time_ms: Optional[float]
    guessing_rate: float  # % of attempts < 2 seconds
    struggle_rate: float  # % of attempts > 60 seconds
    misconception_count: int  # High confidence + wrong


class TopicPerformance(BaseModel):
    """Performance by topic."""
    topic: str
    total_attempts: int
    accuracy: float
    avg_confidence: Optional[float]
    struggling_students: int


class ClassroomAnalytics(BaseModel):
    """Comprehensive classroom analytics."""
    classroom_id: int
    classroom_name: str
    total_students: int
    active_students: int  # Students with attempts in last 7 days
    
    # Overall metrics
    total_attempts: int
    average_accuracy: float
    
    # Psychometric insights
    avg_time_per_question_ms: Optional[float]
    guessing_rate: float
    struggle_rate: float
    
    # Per-student breakdown
    students: List[StudentPerformance]
    
    # Per-topic breakdown
    topics: List[TopicPerformance]


# ============= Endpoints =============

@router.post("/assignments", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    assignment_data: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create homework assignment for a classroom.
    
    Assigns specific questions (by subject/topic/difficulty) to all students.
    """
    # Verify teacher owns this classroom
    classroom = db.query(Classroom).filter(
        Classroom.id == assignment_data.classroom_id,
        Classroom.teacher_id == current_user.id
    ).first()
    
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found or you don't have permission"
        )
    
    # Create assignment
    assignment = Assignment(
        classroom_id=assignment_data.classroom_id,
        title=assignment_data.title,
        description=assignment_data.description,
        subject_filter=assignment_data.subject_filter,
        topic_filter=assignment_data.topic_filter,
        difficulty_filter=assignment_data.difficulty_filter,
        question_count=assignment_data.question_count,
        due_date=assignment_data.due_date
    )
    
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    return assignment


@router.get("/analytics/{classroom_id}", response_model=ClassroomAnalytics)
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
    classroom = db.query(Classroom).filter(
        Classroom.id == classroom_id,
        Classroom.teacher_id == current_user.id
    ).first()
    
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found or you don't have permission"
        )
    
    # Get student IDs in this classroom
    student_ids = [s.id for s in classroom.students]
    
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
        struggling = db.query(func.count(func.distinct(Attempt.user_id))).filter(
            Attempt.user_id.in_(student_ids),
            Attempt.question_id.in_(
                db.query(Question.id).filter(Question.topic == topic)
            )
        ).group_by(Attempt.user_id).having(
            func.avg(case((Attempt.is_correct, 1), else_=0)) < 0.5
        ).scalar() or 0
        
        topics.append(TopicPerformance(
            topic=topic,
            total_attempts=total,
            accuracy=round(accuracy * 100, 2),
            avg_confidence=round(avg_conf, 2) if avg_conf else None,
            struggling_students=struggling
        ))
    
    # Overall class metrics
    all_attempts = db.query(Attempt).filter(Attempt.user_id.in_(student_ids)).all()
    total_attempts = len(all_attempts)
    correct_attempts = sum(1 for a in all_attempts if a.is_correct)
    avg_accuracy = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
    
    # Active students (attempts in last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    active_students = db.query(func.count(func.distinct(Attempt.user_id))).filter(
        Attempt.user_id.in_(student_ids),
        Attempt.attempted_at >= week_ago
    ).scalar() or 0
    
    # Psychometric class averages
    all_times = [a.time_taken_ms for a in all_attempts if a.time_taken_ms]
    avg_time_class = sum(all_times) / len(all_times) if all_times else None
    
    guesses_class = sum(1 for a in all_attempts if a.time_taken_ms and a.time_taken_ms < 2000)
    guessing_rate_class = (guesses_class / total_attempts * 100) if total_attempts > 0 else 0
    
    struggles_class = sum(1 for a in all_attempts if a.time_taken_ms and a.time_taken_ms > 60000)
    struggle_rate_class = (struggles_class / total_attempts * 100) if total_attempts > 0 else 0
    
    return ClassroomAnalytics(
        classroom_id=classroom_id,
        classroom_name=classroom.name,
        total_students=len(student_ids),
        active_students=active_students,
        total_attempts=total_attempts,
        average_accuracy=round(avg_accuracy, 2),
        avg_time_per_question_ms=round(avg_time_class, 2) if avg_time_class else None,
        guessing_rate=round(guessing_rate_class, 2),
        struggle_rate=round(struggle_rate_class, 2),
        students=students_performance,
        topics=topics
    )
