"""Classroom assignment submissions and grading endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.db.session import get_db
from app.models.classroom import Assignment, Submission
from app.models.user import User
from app.models.enums import UserRole
from app.core.security import get_current_user
from app.schemas.schemas import SubmissionCreate, GradeCreate

router = APIRouter()


@router.post("/assignments/{assignment_id}/submit", status_code=status.HTTP_201_CREATED)
async def submit_assignment(
    assignment_id: int, 
    submission_data: SubmissionCreate, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    """Submit an assignment."""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Check if already submitted
    existing = db.query(Submission).filter(
        Submission.assignment_id == assignment_id,
        Submission.student_id == user.id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already submitted this assignment")
    
    new_submission = Submission(
        assignment_id=assignment_id,
        student_id=user.id,
        content_text=submission_data.content_text,
        attachment_url=submission_data.attachment_url
    )
    
    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)
    
    return {"message": "Assignment submitted successfully", "submission_id": new_submission.id}


@router.post("/submissions/{submission_id}/grade", status_code=status.HTTP_200_OK)
async def grade_submission(
    submission_id: int, 
    grade_data: GradeCreate, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    """Grade a submission (Teacher only)."""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    assignment = db.query(Assignment).filter(Assignment.id == submission.assignment_id).first()
    classroom = assignment.classroom
    
    if classroom.teacher_id != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only the teacher can grade submissions")
    
    submission.grade = grade_data.grade
    submission.feedback = grade_data.feedback
    submission.graded_at = func.now()
    submission.graded_by_id = user.id
    
    db.commit()
    
    return {"message": "Submission graded successfully"}
