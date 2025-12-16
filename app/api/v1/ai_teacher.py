"""AI Teacher endpoints: generate quizzes/assignments, grade submissions, insights."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_db
from app.models.classroom import Classroom, Assignment, Submission
from app.models.user import User
from app.core.security import get_current_user
from app.services import ai_service
from app.services.grading_service import auto_grade_submission

router = APIRouter()


class GenerateQuizRequest(BaseModel):
    topic: str
    level: str
    count: int = Field(default=10, ge=1, le=50)
    source_text: Optional[str] = None


class GenerateAssignmentRequest(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class GradeBatchRequest(BaseModel):
    assignment_id: int


@router.post("/teacher/generate-quiz")
async def generate_quiz(req: GenerateQuizRequest, user: User = Depends(get_current_user)):
    if not ai_service.GEMINI_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI service not available")

    prompt = f"""
Act as a WAEC Teacher. Create a {req.count}-question multiple choice quiz for {req.level} students.
Topic: {req.topic}.
{f"Source Material: {req.source_text}" if req.source_text else ""}

Output STRICT JSON format:
[
  {{
    "question": "...",
    "options": ["A","B","C","D"],
    "correct_index": 0,
    "explanation": "..."
  }}
]
"""
    try:
        response = ai_service.model.generate_content(prompt)
        return {"draft": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/teacher/grade-submission/{submission_id}")
async def grade_submission_ai(submission_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    sub = db.query(Submission).filter(Submission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    assignment = db.query(Assignment).filter(Assignment.id == sub.assignment_id).first()
    classroom = db.query(Classroom).filter(Classroom.id == assignment.classroom_id).first()
    # Permission
    if not (user.id == classroom.teacher_id or getattr(user, "is_admin", False)):
        raise HTTPException(status_code=403, detail="Requires teacher or admin")

    # Build marking scheme from assignment description (simple fallback)
    marking_scheme = assignment.description or "Follow rubric"
    question_text = assignment.title
    student_answer = sub.content_text or (sub.attachment_url or "")

    suggestion = await auto_grade_submission(question_text, marking_scheme, student_answer)
    sub.ai_suggested_score = suggestion.get("score")
    sub.ai_feedback_draft = suggestion.get("feedback")
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return {"suggestion": suggestion}


@router.post("/teacher/grade-batch")
async def grade_batch(payload: GradeBatchRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    assignment = db.query(Assignment).filter(Assignment.id == payload.assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    classroom = db.query(Classroom).filter(Classroom.id == assignment.classroom_id).first()
    if not (user.id == classroom.teacher_id or getattr(user, "is_admin", False)):
        raise HTTPException(status_code=403, detail="Requires teacher or admin")

    subs = db.query(Submission).filter(Submission.assignment_id == payload.assignment_id, Submission.is_graded == 0).all()
    results = []
    for s in subs:
        suggestion = await auto_grade_submission(assignment.title, assignment.description or "", s.content_text or s.attachment_url or "")
        s.ai_suggested_score = suggestion.get("score")
        s.ai_feedback_draft = suggestion.get("feedback")
        db.add(s)
        results.append({"submission_id": s.id, "suggestion": suggestion})
    db.commit()
    return {"results": results}


@router.get("/teacher/insights/{classroom_id}")
async def class_insights(classroom_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    if not (user.id == classroom.teacher_id or getattr(user, "is_admin", False)):
        raise HTTPException(status_code=403, detail="Requires teacher or admin")

    # Basic stats
    total_students = len(classroom.students)
    assignments = db.query(Assignment).filter(Assignment.classroom_id == classroom_id).all()
    assignment_stats = []
    for a in assignments:
        subs = db.query(Submission).filter(Submission.assignment_id == a.id).all()
        graded = [s for s in subs if s.is_graded]
        avg = sum([s.grade or 0 for s in graded]) / len(graded) if graded else None
        assignment_stats.append({"assignment_id": a.id, "avg": avg, "total_submissions": len(subs)})

    # If AI available, ask for natural language summary
    if ai_service.GEMINI_AVAILABLE:
        try:
            summary_input = f"Class {classroom.name}: total_students={total_students}. Assignment stats: {assignment_stats}"
            response = ai_service.model.generate_content(f"Provide a short teacher-facing insight for the following data: {summary_input}")
            return {"insight": response.text.strip(), "stats": {"total_students": total_students, "assignments": assignment_stats}}
        except Exception:
            pass

    return {"stats": {"total_students": total_students, "assignments": assignment_stats}}
