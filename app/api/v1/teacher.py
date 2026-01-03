"""Teacher API endpoints - Classroom management and student analytics."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models.user import User
from app.models.classroom import Classroom, Assignment, classroom_students, ClassroomMaterial
from app.models.asset import Asset
from app.models.progress import Attempt
from app.models.question import Question
from app.services.storage import StorageService, AssetType
from app.services.teacher_ai_assistant import process_teacher_command
from fastapi import UploadFile, File, Query
from app.models.enums import Subject, Topic, DifficultyLevel, AssignmentType, AssignmentStatus, GradeLevel
from app.core.security import get_current_user
from app.schemas.schemas import (
    TeacherAIRequest, 
    TeacherAIResponse, 
    ApproveQuizRequest
)

router = APIRouter()


# ============= Schemas =============

class ClassroomCreate(BaseModel):
    """Schema for creating a classroom."""
    name: str = Field(..., min_length=3, max_length=100, description="Classroom name")
    description: Optional[str] = Field(None, max_length=500)
    subject: Optional[Subject] = None
    grade_level: Optional[GradeLevel] = None


class ClassroomResponse(BaseModel):
    """Schema for classroom responses."""
    id: int
    name: str
    description: Optional[str]
    join_code: str
    is_active: int
    student_count: int
    subject: Optional[Subject] = None
    grade_level: Optional[GradeLevel] = None
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
    subject_filter: Optional[Subject] = None
    topic_filter: Optional[Topic] = None
    difficulty_filter: Optional[DifficultyLevel] = None
    question_count: int = Field(default=10, ge=1, le=50)
    due_date: Optional[datetime] = None


class AssignmentResponse(BaseModel):
    """Schema for assignment responses."""
    id: int
    classroom_id: int
    title: str
    description: Optional[str]
    subject_filter: Optional[Subject] = None
    topic_filter: Optional[Topic] = None
    question_count: int
    due_date: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class StudentPerformance(BaseModel):
    """Individual student performance in a classroom."""
    user_id: int
    student_id: int  # Alias for user_id for backward compatibility
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
    class_accuracy: float  # Alias for average_accuracy for backward compatibility
    average_confidence: float
    
    # Psychometric insights
    avg_time_per_question_ms: Optional[float]
    guessing_rate: float
    struggle_rate: float
    
    # Per-student breakdown
    students: List[StudentPerformance]
    student_performance: List[StudentPerformance] = []  # Alias for backward compatibility
    
    # Per-topic breakdown
    topics: List[TopicPerformance]
    topic_performance: List[TopicPerformance] = []  # Alias for backward compatibility


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
    
    return analytics


# ============= Classroom Materials =============

@router.post("/classrooms/{classroom_id}/materials")
async def upload_classroom_material(
    classroom_id: int,
    title: str = Query(..., min_length=3),
    description: Optional[str] = Query(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload study materials (PDFs, books, images) for a classroom.
    
    Only the classroom teacher can upload materials.
    """
    # Verify classroom ownership
    classroom = db.query(Classroom).filter(
        Classroom.id == classroom_id,
        Classroom.teacher_id == current_user.id
    ).first()
    
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the classroom teacher can upload materials"
        )
    
    # Determine asset type from filename/content_type
    asset_type = "document"
    if file.content_type.startswith("image/"):
        asset_type = "image"
    elif file.content_type == "application/pdf":
        asset_type = "pdf"
        
    # Upload to storage
    storage_service = StorageService()
    url = storage_service.upload_image(
        file.file,
        AssetType.QUESTION_DIAGRAM, # Reusing enum for now or add MATERIAL type
        file.filename,
        user_id=current_user.id
    )
    
    # Create central asset record
    asset = Asset(
        filename=file.filename,
        url=url,
        asset_type=asset_type,
        mime_type=file.content_type,
        uploaded_by_id=current_user.id
    )
    db.add(asset)
    db.flush() # Get asset ID
    
    # Create classroom material record
    material = ClassroomMaterial(
        classroom_id=classroom_id,
        uploaded_by_id=current_user.id,
        asset_id=asset.id,
        title=title,
        description=description,
        url=url
    )
    db.add(material)
    db.commit()
    
    return {
        "message": "Material uploaded successfully",
        "material_id": material.id,
        "asset_id": asset.id,
        "url": url
    }

@router.get("/classrooms/{classroom_id}/materials")
async def get_classroom_materials(
    classroom_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all materials for a classroom."""
    # Verify membership (teacher or student)
    is_teacher = db.query(Classroom).filter(
        Classroom.id == classroom_id,
        Classroom.teacher_id == current_user.id
    ).first()
    
    is_student = db.query(classroom_students).filter(
        classroom_students.c.classroom_id == classroom_id,
        classroom_students.c.student_id == current_user.id
    ).first()
    
    if not is_teacher and not is_student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a member of this classroom to view materials"
        )
    
    materials = db.query(ClassroomMaterial).filter(
        ClassroomMaterial.classroom_id == classroom_id
    ).all()
    
    return materials


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
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found"
        )
    
    if classroom.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this classroom's analytics"
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
            class_accuracy=0.0,
            average_confidence=0.0,
            avg_time_per_question_ms=None,
            guessing_rate=0.0,
            struggle_rate=0.0,
            students=[],
            student_performance=[],
            topics=[],
            topic_performance=[]
        )
    
    # Calculate per-student performance
    students_performance = []
    for student_id in student_ids:
        user = db.query(User).filter(User.id == student_id).first()
        
        attempts = db.query(Attempt).filter(Attempt.user_id == student_id).all()
        
        if not attempts:
            students_performance.append(StudentPerformance(
                user_id=student_id,
                student_id=student_id,
                full_name=user.full_name or user.username or "Unknown",
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
            student_id=student_id,
            full_name=user.full_name or user.username or "Unknown",
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
        struggling_query = db.query(Attempt.user_id).filter(
            Attempt.user_id.in_(student_ids),
            Attempt.question_id.in_(
                db.query(Question.id).filter(Question.topic == topic)
            )
        ).group_by(Attempt.user_id).having(
            func.avg(case((Attempt.is_correct, 1), else_=0)) < 0.5
        )
        struggling = db.query(func.count()).select_from(struggling_query.subquery()).scalar() or 0
        
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
    
    # Average confidence
    confidences = [a.confidence_level for a in all_attempts if a.confidence_level is not None]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    
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
        class_accuracy=round(avg_accuracy, 2),
        average_confidence=round(avg_confidence, 2),
        avg_time_per_question_ms=round(avg_time_class, 2) if avg_time_class else None,
        guessing_rate=round(guessing_rate_class, 2),
        struggle_rate=round(struggle_rate_class, 2),
        students=students_performance,
        student_performance=students_performance,
        topics=topics,
        topic_performance=topics
    )


# ============= AI Assistant Endpoints =============

@router.post("/ai-assistant", response_model=TeacherAIResponse)
async def teacher_ai_assistant(
    request: TeacherAIRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI Assistant for teachers - natural language classroom management.
    
    The teacher can communicate in natural language to:
    - Create quizzes: "Create a quiz on Quadratic Equations for SS2"
    - Analyze performance: "How is my Physics class doing?"
    - Identify struggling students: "Which students need help?"
    - Generate reports: "Give me a summary of this week"
    
    The AI will:
    1. Parse the natural language request
    2. Identify the intent and extract parameters
    3. Execute the appropriate action
    4. Return structured data for teacher review
    
    For quiz creation, questions are returned as draft requiring teacher approval
    before being sent to students.
    
    Examples:
        POST /api/v1/teacher/ai-assistant
        {
            "message": "Create a 10-question quiz on Algebra for my SS1 class",
            "classroom_id": 5
        }
        
        POST /api/v1/teacher/ai-assistant
        {
            "message": "Which students are struggling in classroom 5?",
            "classroom_id": 5
        }
    """
    # Verify teacher role
    from app.models.enums import UserRole
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


@router.post("/ai-assistant/approve-quiz", response_model=AssignmentResponse)
async def approve_and_send_quiz(
    request: ApproveQuizRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve AI-generated quiz and send to students.
    
    After reviewing the quiz draft from the AI assistant, teacher can:
    1. Select which questions to include
    2. Set title, description, and due date
    3. Assign points per question
    4. Send to classroom
    
    This creates a new Assignment with the selected questions.
    Students will see this in their assignments list and can start answering.
    
    Example:
        POST /api/v1/teacher/ai-assistant/approve-quiz
        {
            "question_ids": [1, 5, 10, 15, 20],
            "classroom_id": 5,
            "title": "Algebra Quiz - Week 3",
            "description": "Practice on quadratic equations",
            "due_date": "2025-01-15T23:59:59Z",
            "points_per_question": 10
        }
    """
    # Verify teacher role
    from app.models.enums import UserRole
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
    
    # TODO: Store specific question IDs in a separate table or JSON field
    # For now, students will practice from the question pool matching the filters
    
    return AssignmentResponse(
        id=assignment.id,
        classroom_id=assignment.classroom_id,
        title=assignment.title,
        description=assignment.description,
        subject_filter=assignment.subject_filter,
        topic_filter=assignment.topic_filter,
        question_count=assignment.question_count,
        due_date=assignment.due_date,
        created_at=assignment.created_at
    )

