"""Base classroom CRUD endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import logging

from app.db.session import get_db
from app.models.classroom import Classroom, classroom_students
from app.models.user import User
from app.models.enums import UserRole
from app.core.security import get_current_user
from app.schemas.schemas import ClassroomCreate, ClassroomResponse, ClassroomUpdate

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
