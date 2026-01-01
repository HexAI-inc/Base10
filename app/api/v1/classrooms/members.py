"""Classroom membership (join/leave/list) endpoints."""
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
from app.schemas.schemas import ClassroomJoin, UserResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/join", status_code=status.HTTP_200_OK)
async def join_classroom(join_data: ClassroomJoin, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Join a classroom using a join code."""
    classroom = db.query(Classroom).filter(Classroom.join_code == join_data.join_code).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found with this code")
    
    if not classroom.is_active:
        raise HTTPException(status_code=400, detail="This classroom is no longer active")
    
    # Check if already a member
    existing = db.query(classroom_students).filter(
        classroom_students.c.classroom_id == classroom.id,
        classroom_students.c.student_id == user.id
    ).first()
    
    if existing:
        return {"message": "Already a member of this classroom", "classroom_id": classroom.id}
    
    # Add to classroom
    db.execute(
        classroom_students.insert().values(
            classroom_id=classroom.id,
            student_id=user.id
        )
    )
    db.commit()
    
    logger.info(f"🎓 Student {user.id} joined classroom: {classroom.name}")
    
    return {"message": f"Successfully joined {classroom.name}", "classroom_id": classroom.id}


@router.get("/{classroom_id}/members", response_model=List[UserResponse])
async def list_classroom_members(classroom_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """List all students in a classroom (Teacher only)."""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    if classroom.teacher_id != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only the teacher can view the member list")
    
    students = db.query(User).join(
        classroom_students,
        User.id == classroom_students.c.student_id
    ).filter(
        classroom_students.c.classroom_id == classroom_id
    ).all()
    
    return students
