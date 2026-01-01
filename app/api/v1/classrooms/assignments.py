"""Classroom assignments endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.classroom import Classroom, Assignment
from app.models.user import User
from app.models.enums import UserRole
from app.core.security import get_current_user
from app.schemas.schemas import AssignmentCreate, AssignmentResponse, AssignmentUpdate

router = APIRouter()


@router.get("/{classroom_id}/assignments", response_model=List[AssignmentResponse])
async def get_classroom_assignments(classroom_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get all assignments in a classroom."""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    assignments = db.query(Assignment).filter(
        Assignment.classroom_id == classroom_id
    ).all()
    
    return assignments


@router.post("/{classroom_id}/assignments", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    classroom_id: int, 
    assignment_data: AssignmentCreate, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    """Create an assignment in a classroom (Teacher only)."""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    if classroom.teacher_id != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only the teacher can create assignments")
    
    new_assignment = Assignment(
        classroom_id=classroom_id,
        title=assignment_data.title,
        description=assignment_data.description,
        subject_filter=assignment_data.subject_filter,
        topic_filter=assignment_data.topic_filter,
        difficulty_filter=assignment_data.difficulty_filter,
        question_count=assignment_data.question_count,
        due_date=assignment_data.due_date
    )
    
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    
    return new_assignment
