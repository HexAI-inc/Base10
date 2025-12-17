"""Classroom LMS router: stream, materials, members, assignments, submissions, grading."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.db.session import get_db
from app.models.classroom import Classroom, ClassroomPost, ClassroomMaterial, Assignment, Submission, classroom_students
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter()


# ---------------- Schemas ----------------
class StreamPostCreate(BaseModel):
    content: str = Field(..., min_length=1)
    attachment_url: Optional[str] = None


class StreamPostResponse(BaseModel):
    id: int
    classroom_id: int
    author_id: int
    content: str
    post_type: str
    attachment_url: Optional[str]
    parent_post_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class MaterialCreate(BaseModel):
    title: str
    description: Optional[str] = None
    asset_id: Optional[str] = None
    url: Optional[str] = None


class MaterialResponse(BaseModel):
    id: int
    classroom_id: int
    uploaded_by_id: int
    title: Optional[str]
    description: Optional[str]
    asset_id: Optional[str]
    url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ManualAssignmentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    points: Optional[int] = 100


class SubmissionCreate(BaseModel):
    content_text: Optional[str] = None
    attachment_url: Optional[str] = None


class GradeCreate(BaseModel):
    grade: int = Field(..., ge=0, le=100)
    feedback: Optional[str] = None


# ---------------- Helpers ----------------

def require_teacher_or_admin(classroom: Classroom, user: User):
    if not (user.id == classroom.teacher_id or getattr(user, "is_admin", False)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires classroom teacher or admin")


# ---------------- Endpoints ----------------
@router.get("/classrooms/{classroom_id}/stream", response_model=List[StreamPostResponse])
async def get_class_stream(classroom_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    posts = db.query(ClassroomPost).filter(ClassroomPost.classroom_id == classroom_id).order_by(ClassroomPost.created_at.desc()).all()
    return posts


@router.post("/classrooms", status_code=status.HTTP_201_CREATED)
async def create_classroom(classroom_data: dict, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from app.models.classroom import Classroom
    join_code = Classroom.generate_join_code()
    classroom = Classroom(
        teacher_id=user.id,
        name=classroom_data.get('name'),
        description=classroom_data.get('description'),
        join_code=join_code
    )
    db.add(classroom)
    db.commit()
    db.refresh(classroom)
    return {"id": classroom.id, "join_code": classroom.join_code}


@router.get("/classrooms", response_model=List[dict])
async def list_classrooms(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    classrooms = db.query(
        Classroom,
        func.count(classroom_students.c.student_id).label('student_count')
    ).outerjoin(
        classroom_students,
        Classroom.id == classroom_students.c.classroom_id
    ).filter(
        Classroom.teacher_id == user.id
    ).group_by(
        Classroom.id
    ).all()

    return [
        {"id": classroom.id, "name": classroom.name, "description": classroom.description, "join_code": classroom.join_code, "student_count": count}
        for classroom, count in classrooms
    ]


@router.get("/classrooms/{classroom_id}")
async def get_classroom(classroom_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get classroom details by ID. Teachers see their own classrooms, students see classrooms they're enrolled in."""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    # Check permissions: teacher who owns it OR student enrolled in it
    is_teacher = classroom.teacher_id == user.id
    is_student = user in classroom.students
    
    if not (is_teacher or is_student):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get student count
    student_count = db.query(func.count(classroom_students.c.student_id)).filter(
        classroom_students.c.classroom_id == classroom_id
    ).scalar() or 0
    
    return {
        "id": classroom.id,
        "name": classroom.name,
        "description": classroom.description,
        "subject": classroom.subject,
        "grade_level": classroom.grade_level,
        "join_code": classroom.join_code if is_teacher else None,  # Only teachers see join code
        "teacher_id": classroom.teacher_id,
        "teacher_name": classroom.teacher.full_name if classroom.teacher else None,
        "is_active": classroom.is_active,
        "student_count": student_count,
        "created_at": classroom.created_at.isoformat(),
        "is_teacher": is_teacher,
        "is_student": is_student
    }


@router.post("/classrooms/join")
async def join_classroom(join_data: dict, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    classroom = db.query(Classroom).filter(
        Classroom.join_code == join_data.get('join_code'),
        Classroom.is_active == True
    ).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found or inactive")

    if user in classroom.students:
        return {"message": "Already enrolled"}

    # add to association table
    stmt = classroom_students.insert().values(classroom_id=classroom.id, student_id=user.id)
    db.execute(stmt)
    db.commit()
    return {"message": "Joined", "classroom_id": classroom.id}


@router.post("/classrooms/{classroom_id}/announce", response_model=StreamPostResponse)
async def post_announcement(classroom_id: int, payload: StreamPostCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    require_teacher_or_admin(classroom, user)

    post = ClassroomPost(
        classroom_id=classroom_id,
        author_id=user.id,
        content=payload.content,
        post_type="announcement",
        attachment_url=payload.attachment_url,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.post("/classrooms/{classroom_id}/stream/{post_id}/comment", response_model=StreamPostResponse)
async def comment_on_post(classroom_id: int, post_id: int, payload: StreamPostCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    parent = db.query(ClassroomPost).filter(ClassroomPost.id == post_id, ClassroomPost.classroom_id == classroom_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Post not found")
    # Allow students and teachers to comment
    comment = ClassroomPost(
        classroom_id=classroom_id,
        author_id=user.id,
        content=payload.content,
        post_type="comment",
        attachment_url=payload.attachment_url,
        parent_post_id=parent.id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/classrooms/{classroom_id}/stream/{post_id}")
async def delete_post(classroom_id: int, post_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    post = db.query(ClassroomPost).filter(ClassroomPost.id == post_id, ClassroomPost.classroom_id == classroom_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    require_teacher_or_admin(classroom, user)
    db.delete(post)
    db.commit()
    return {"detail": "deleted"}


@router.post("/classrooms/{classroom_id}/materials", response_model=MaterialResponse)
async def upload_material(classroom_id: int, payload: MaterialCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    require_teacher_or_admin(classroom, user)
    material = ClassroomMaterial(
        classroom_id=classroom_id,
        uploaded_by_id=user.id,
        asset_id=payload.asset_id,
        title=payload.title,
        description=payload.description,
        url=payload.url
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


@router.get("/classrooms/{classroom_id}/materials", response_model=List[MaterialResponse])
async def list_materials(classroom_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    materials = db.query(ClassroomMaterial).filter(ClassroomMaterial.classroom_id == classroom_id).order_by(ClassroomMaterial.created_at.desc()).all()
    return materials


@router.get("/classrooms/{classroom_id}/assignments")
async def get_classroom_assignments(classroom_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get all assignments for a classroom. Teachers see all, students see published assignments."""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    # Check permissions: teacher who owns it OR student enrolled in it
    is_teacher = classroom.teacher_id == user.id
    is_student = user in classroom.students
    
    if not (is_teacher or is_student):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Build query
    query = db.query(Assignment).filter(Assignment.classroom_id == classroom_id)
    
    # Students only see published assignments
    if not is_teacher:
        query = query.filter(Assignment.status == "published")
    
    assignments = query.order_by(Assignment.created_at.desc()).all()
    
    # Get submission counts for teachers
    result = []
    for assignment in assignments:
        assignment_data = {
            "id": assignment.id,
            "classroom_id": assignment.classroom_id,
            "title": assignment.title,
            "description": assignment.description,
            "assignment_type": assignment.assignment_type,
            "max_points": assignment.max_points,
            "due_date": assignment.due_date.isoformat() if assignment.due_date else None,
            "is_ai_generated": assignment.is_ai_generated,
            "status": assignment.status,
            "created_at": assignment.created_at.isoformat()
        }
        
        # Add submission stats for teachers
        if is_teacher:
            from app.models.classroom import Submission
            total_submissions = db.query(func.count(Submission.id)).filter(
                Submission.assignment_id == assignment.id
            ).scalar() or 0
            
            graded_submissions = db.query(func.count(Submission.id)).filter(
                Submission.assignment_id == assignment.id,
                Submission.is_graded == True
            ).scalar() or 0
            
            assignment_data["submission_count"] = total_submissions
            assignment_data["graded_count"] = graded_submissions
        else:
            # Check if student has submitted
            from app.models.classroom import Submission
            student_submission = db.query(Submission).filter(
                Submission.assignment_id == assignment.id,
                Submission.student_id == user.id
            ).first()
            
            assignment_data["has_submitted"] = student_submission is not None
            assignment_data["submission_id"] = student_submission.id if student_submission else None
            assignment_data["is_graded"] = student_submission.is_graded if student_submission else False
            assignment_data["final_score"] = student_submission.final_score if student_submission else None
        
        result.append(assignment_data)
    
    return result


@router.get("/classrooms/{classroom_id}/members")
async def get_members(classroom_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    teacher = db.query(User).filter(User.id == classroom.teacher_id).first()
    students = classroom.students
    return {"teacher": teacher, "students": students}


@router.delete("/classrooms/{classroom_id}/members/{user_id}")
async def remove_member(classroom_id: int, user_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    require_teacher_or_admin(classroom, user)
    stmt = classroom_students.delete().where(classroom_students.c.classroom_id == classroom_id, classroom_students.c.student_id == user_id)
    db.execute(stmt)
    db.commit()
    return {"detail": "removed"}


@router.post("/classrooms/{classroom_id}/invite")
async def reset_join_code(classroom_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    require_teacher_or_admin(classroom, user)
    classroom.join_code = Classroom.generate_join_code()
    db.add(classroom)
    db.commit()
    db.refresh(classroom)
    return {"join_code": classroom.join_code}


@router.post("/classrooms/{classroom_id}/assignments/manual")
async def create_manual_assignment(classroom_id: int, payload: ManualAssignmentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    require_teacher_or_admin(classroom, user)
    assignment = Assignment(
        classroom_id=classroom_id,
        title=payload.title,
        description=payload.description,
        due_date=payload.due_date,
        max_points=payload.points,
        assignment_type="manual",
        status="published"
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return {"id": assignment.id, "detail": "created"}


@router.post("/classrooms/assignments/{assignment_id}/submit")
async def submit_assignment(assignment_id: int, payload: SubmissionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    # verify user is member of class
    classroom = db.query(Classroom).filter(Classroom.id == assignment.classroom_id).first()
    if user not in classroom.students and user.id != classroom.teacher_id:
        raise HTTPException(status_code=403, detail="Not a member of the classroom")

    sub = Submission(
        assignment_id=assignment_id,
        student_id=user.id,
        content_text=payload.content_text,
        attachment_url=payload.attachment_url
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return {"id": sub.id, "detail": "submitted"}


@router.get("/classrooms/assignments/{assignment_id}/submissions")
async def list_submissions(assignment_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    classroom = db.query(Classroom).filter(Classroom.id == assignment.classroom_id).first()
    require_teacher_or_admin(classroom, user)
    subs = db.query(Submission).filter(Submission.assignment_id == assignment_id).order_by(Submission.submitted_at.desc()).all()
    return subs


@router.post("/classrooms/submissions/{submission_id}/grade")
async def grade_submission(submission_id: int, payload: GradeCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    sub = db.query(Submission).filter(Submission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    assignment = db.query(Assignment).filter(Assignment.id == sub.assignment_id).first()
    classroom = db.query(Classroom).filter(Classroom.id == assignment.classroom_id).first()
    require_teacher_or_admin(classroom, user)
    sub.grade = payload.grade
    sub.feedback = payload.feedback
    sub.is_graded = 1
    sub.status = "graded"
    sub.graded_at = datetime.utcnow()
    db.add(sub)
    db.commit()
    db.refresh(sub)
    # TODO: Trigger notification / sync flag for student
    return {"detail": "graded", "id": sub.id}


@router.get("/student/grades")
async def student_grades(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    subs = db.query(Submission).filter(Submission.student_id == user.id, Submission.is_graded == 1).order_by(Submission.graded_at.desc()).all()
    return subs
