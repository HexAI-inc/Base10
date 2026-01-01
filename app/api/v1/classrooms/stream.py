"""Classroom stream (posts and comments) endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.session import get_db
from app.models.classroom import Classroom, ClassroomPost
from app.models.user import User
from app.core.security import get_current_user
from app.schemas.schemas import StreamPostCreate, StreamPostResponse

router = APIRouter()


@router.get("/{classroom_id}/stream", response_model=List[StreamPostResponse])
async def get_class_stream(classroom_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get all posts in a classroom stream."""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    posts = db.query(ClassroomPost).filter(
        ClassroomPost.classroom_id == classroom_id
    ).order_by(ClassroomPost.created_at.desc()).all()
    
    return posts


@router.post("/{classroom_id}/stream", response_model=StreamPostResponse, status_code=status.HTTP_201_CREATED)
async def create_stream_post(
    classroom_id: int, 
    post_data: StreamPostCreate, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    """Create a new post in the classroom stream."""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    # Check if user is teacher or student in this classroom
    from app.models.classroom import classroom_students
    is_student = db.query(classroom_students).filter(
        classroom_students.c.classroom_id == classroom_id,
        classroom_students.c.student_id == user.id
    ).first()
    
    if classroom.teacher_id != user.id and not is_student:
        raise HTTPException(status_code=403, detail="Not a member of this classroom")
    
    new_post = ClassroomPost(
        classroom_id=classroom_id,
        author_id=user.id,
        content=post_data.content,
        attachment_url=post_data.attachment_url,
        post_type="announcement" if classroom.teacher_id == user.id else "discussion"
    )
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return new_post
