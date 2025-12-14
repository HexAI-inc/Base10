"""Question quality reporting endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.db.session import get_db
from app.models.user import User
from app.models.question import Question
from app.models.report import QuestionReport, ReportReason
from app.core.security import get_current_user

router = APIRouter()


class ReportQuestionRequest(BaseModel):
    """Schema for reporting a question."""
    reason: ReportReason
    comment: Optional[str] = None


class ReportResponse(BaseModel):
    """Response after reporting a question."""
    id: int
    question_id: int
    reason: str
    status: str
    message: str


@router.post("/{question_id}/report", response_model=ReportResponse, status_code=201)
async def report_question(
    question_id: int,
    report: ReportQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Report a question for quality issues.
    
    Crowdsourced QA:
    - Students report typos, wrong answers, unclear questions
    - Admin dashboard shows most-reported questions
    - Helps maintain quality at scale (4,000+ questions)
    
    Example:
        POST /api/v1/questions/42/report
        {
            "reason": "Wrong Answer",
            "comment": "Option B is correct, not A. See Physics textbook page 145"
        }
    """
    # Verify question exists
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Check if user already reported this question
    existing_report = db.query(QuestionReport).filter(
        QuestionReport.question_id == question_id,
        QuestionReport.user_id == current_user.id
    ).first()
    
    if existing_report:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reported this question"
        )
    
    # Create report
    new_report = QuestionReport(
        question_id=question_id,
        user_id=current_user.id,
        reason=report.reason,
        comment=report.comment,
        status="pending"
    )
    
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    return ReportResponse(
        id=new_report.id,
        question_id=question_id,
        reason=report.reason.value,
        status=new_report.status,
        message="Thank you for reporting this issue. Our team will review it."
    )


@router.get("/{question_id}/reports")
async def get_question_reports(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all reports for a question.
    
    Note: In production, restrict this to admin users only.
    For now, any authenticated user can see reports.
    """
    reports = db.query(QuestionReport).filter(
        QuestionReport.question_id == question_id
    ).all()
    
    return {
        "question_id": question_id,
        "total_reports": len(reports),
        "reports": [
            {
                "id": r.id,
                "reason": r.reason.value,
                "comment": r.comment,
                "status": r.status,
                "created_at": r.created_at
            }
            for r in reports
        ]
    }
