"""Classroom LMS router: stream, materials, members, assignments, submissions, grading."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
import logging

from app.db.session import get_db
from app.models.classroom import Classroom, ClassroomPost, ClassroomMaterial, Assignment, Submission, classroom_students
from app.models.user import User
from app.core.security import get_current_user
from app.services.comms_service import CommunicationService, MessageType, MessagePriority

logger = logging.getLogger(__name__)

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


class ClassroomUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    subject: Optional[str] = Field(None, max_length=100)
    grade_level: Optional[str] = Field(None, max_length=50)


class AssignmentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    subject_filter: Optional[str] = None
    topic_filter: Optional[str] = None
    difficulty_filter: Optional[str] = None
    question_count: Optional[int] = Field(None, gt=0)
    assignment_type: Optional[str] = None
    max_points: Optional[int] = Field(None, gt=0)
    status: Optional[str] = None
    due_date: Optional[datetime] = None


class MaterialUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
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
    
    # Add teacher classrooms with full details
    for classroom, count in teacher_classrooms:
        result.append({
            "id": classroom.id,
            "name": classroom.name,
            "description": classroom.description,
            "subject": classroom.subject,
            "grade_level": classroom.grade_level,
            "join_code": classroom.join_code,  # Teachers see join code
            "student_count": count,
            "role": "teacher",
            "is_active": classroom.is_active,
            "created_at": classroom.created_at.isoformat()
        })
    
    # Add student classrooms (without join code)
    for classroom, count in student_classrooms:
        # Get teacher info
        teacher = db.query(User).filter(User.id == classroom.teacher_id).first()
        teacher_name = teacher.full_name if teacher else "Unknown"
        
        result.append({
            "id": classroom.id,
            "name": classroom.name,
            "description": classroom.description,
            "subject": classroom.subject,
            "grade_level": classroom.grade_level,
            "teacher_name": teacher_name,
            "student_count": count,
            "role": "student",
            "is_active": classroom.is_active,
            "created_at": classroom.created_at.isoformat()
        })
    
    return result


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


@router.put("/classrooms/{classroom_id}")
async def update_classroom(
    classroom_id: int, 
    update_data: ClassroomUpdate,
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    """Update classroom details. Only the teacher can update."""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    # Only teacher can update
    if classroom.teacher_id != user.id:
        raise HTTPException(status_code=403, detail="Only the teacher can update this classroom")
    
    # Update fields that are provided
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(classroom, field, value)
    
    db.commit()
    db.refresh(classroom)
    
    return {
        "id": classroom.id,
        "name": classroom.name,
        "description": classroom.description,
        "subject": classroom.subject,
        "grade_level": classroom.grade_level,
        "is_active": classroom.is_active,
        "updated_at": classroom.updated_at.isoformat()
    }


@router.delete("/classrooms/{classroom_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_classroom(
    classroom_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Soft delete a classroom by setting is_active to False. Only the teacher can delete."""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    # Only teacher can delete
    if classroom.teacher_id != user.id:
        raise HTTPException(status_code=403, detail="Only the teacher can delete this classroom")
    
    # Soft delete
    classroom.is_active = False
    db.commit()
    
    return None


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
    
    # 🔔 Notify all students in the classroom
    try:
        comms = CommunicationService()
        students = classroom.students
        
        # Truncate content for notification (first 100 chars)
        preview = payload.content[:100] + "..." if len(payload.content) > 100 else payload.content
        
        for student in students:
            comms.send_notification(
                user_id=student.id,
                message_type=MessageType.ACHIEVEMENT_UNLOCKED,  # Using existing type
                priority=MessagePriority.MEDIUM,
                title=f"📢 {classroom.name}",
                body=f"{user.full_name or user.username}: {preview}",
                data={
                    "type": "classroom_announcement",
                    "classroom_id": classroom_id,
                    "post_id": post.id,
                    "classroom_name": classroom.name
                },
                user_phone=student.phone_number,
                user_email=student.email,
                has_app_installed=student.has_app_installed or False
            )
        
        logger.info(f"📢 Announcement notifications sent to {len(students)} students in classroom {classroom_id}")
    except Exception as e:
        logger.error(f"❌ Failed to send announcement notifications: {e}")
        # Don't fail the request if notifications fail
    
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


@router.put("/classrooms/materials/{material_id}")
async def update_material(
    material_id: int,
    update_data: MaterialUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Update material details. Only the teacher can update."""
    # Get the material
    material = db.query(ClassroomMaterial).filter(ClassroomMaterial.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    # Check if user is the teacher of the classroom
    classroom = db.query(Classroom).filter(Classroom.id == material.classroom_id).first()
    if not classroom or classroom.teacher_id != user.id:
        raise HTTPException(status_code=403, detail="Only the teacher can update this material")
    
    # Update fields that are provided
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(material, field, value)
    
    db.commit()
    db.refresh(material)
    
    return {
        "id": material.id,
        "title": material.title,
        "description": material.description,
        "asset_id": material.asset_id,
        "url": material.url,
        "material_type": material.material_type,
        "created_at": material.created_at.isoformat()
    }


@router.delete("/classrooms/materials/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Delete a material. Only the teacher can delete."""
    # Get the material
    material = db.query(ClassroomMaterial).filter(ClassroomMaterial.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    # Check if user is the teacher of the classroom
    classroom = db.query(Classroom).filter(Classroom.id == material.classroom_id).first()
    if not classroom or classroom.teacher_id != user.id:
        raise HTTPException(status_code=403, detail="Only the teacher can delete this material")
    
    # Hard delete
    db.delete(material)
    db.commit()
    
    return None


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
    """Get all members (teacher + students) in a classroom with detailed info."""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    # Check permissions: teacher or enrolled student can view members
    is_teacher = classroom.teacher_id == user.id
    is_student = user in classroom.students
    
    if not (is_teacher or is_student):
        raise HTTPException(status_code=403, detail="Not authorized to view classroom members")
    
    # Get teacher info
    teacher = db.query(User).filter(User.id == classroom.teacher_id).first()
    teacher_data = {
        "id": teacher.id,
        "full_name": teacher.full_name,
        "username": teacher.username,
        "email": teacher.email if is_teacher else None,  # Only teacher sees other's emails
        "role": "teacher",
        "avatar_url": teacher.avatar_url
    } if teacher else None
    
    # Get students with join dates and activity
    students_data = []
    for student in classroom.students:
        # Get join date from association table
        join_record = db.query(classroom_students).filter(
            classroom_students.c.classroom_id == classroom_id,
            classroom_students.c.student_id == student.id
        ).first()
        
        # Get student's submission count (activity indicator)
        from app.models.classroom import Submission
        submission_count = db.query(func.count(Submission.id)).join(
            Assignment,
            Submission.assignment_id == Assignment.id
        ).filter(
            Assignment.classroom_id == classroom_id,
            Submission.student_id == student.id
        ).scalar() or 0
        
        students_data.append({
            "id": student.id,
            "full_name": student.full_name or student.username,
            "username": student.username,
            "email": student.email if is_teacher else None,  # Only teacher sees emails
            "role": "student",
            "avatar_url": student.avatar_url,
            "joined_at": join_record.joined_at.isoformat() if join_record else None,
            "submission_count": submission_count,
            "is_active": student.is_active
        })
    
    # Sort students by name
    students_data.sort(key=lambda x: x["full_name"].lower())
    
    return {
        "classroom_id": classroom_id,
        "classroom_name": classroom.name,
        "teacher": teacher_data,
        "students": students_data,
        "total_students": len(students_data)
    }


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
    
    # 🔔 Notify all students about new assignment
    try:
        comms = CommunicationService()
        students = classroom.students
        
        # Format due date for notification
        due_text = f" (Due: {payload.due_date.strftime('%b %d')})" if payload.due_date else ""
        
        for student in students:
            # Use HIGH priority if due within 24 hours, otherwise MEDIUM
            priority = MessagePriority.HIGH if (payload.due_date and (payload.due_date - datetime.utcnow()).days < 1) else MessagePriority.MEDIUM
            
            comms.send_notification(
                user_id=student.id,
                message_type=MessageType.ACHIEVEMENT_UNLOCKED,  # Using existing type
                priority=priority,
                title=f"📝 New Assignment: {classroom.name}",
                body=f"{payload.title}{due_text}",
                data={
                    "type": "assignment_created",
                    "classroom_id": classroom_id,
                    "assignment_id": assignment.id,
                    "classroom_name": classroom.name,
                    "due_date": payload.due_date.isoformat() if payload.due_date else None
                },
                user_phone=student.phone_number,
                user_email=student.email,
                has_app_installed=student.has_app_installed or False
            )
        
        logger.info(f"📝 Assignment notifications sent to {len(students)} students in classroom {classroom_id}")
    except Exception as e:
        logger.error(f"❌ Failed to send assignment notifications: {e}")
        # Don't fail the request if notifications fail
    
    return {"id": assignment.id, "detail": "created"}


@router.put("/classrooms/assignments/{assignment_id}")
async def update_assignment(
    assignment_id: int,
    update_data: AssignmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Update assignment details. Only the teacher can update."""
    # Get the assignment
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Check if user is the teacher of the classroom
    classroom = db.query(Classroom).filter(Classroom.id == assignment.classroom_id).first()
    if not classroom or classroom.teacher_id != user.id:
        raise HTTPException(status_code=403, detail="Only the teacher can update this assignment")
    
    # Update fields that are provided
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(assignment, field, value)
    
    db.commit()
    db.refresh(assignment)
    
    return {
        "id": assignment.id,
        "title": assignment.title,
        "description": assignment.description,
        "subject_filter": assignment.subject_filter,
        "topic_filter": assignment.topic_filter,
        "difficulty_filter": assignment.difficulty_filter,
        "question_count": assignment.question_count,
        "assignment_type": assignment.assignment_type,
        "max_points": assignment.max_points,
        "status": assignment.status,
        "due_date": assignment.due_date.isoformat() if assignment.due_date else None,
        "updated_at": assignment.updated_at.isoformat()
    }


@router.delete("/classrooms/assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Delete an assignment. Only the teacher can delete."""
    # Get the assignment
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Check if user is the teacher of the classroom
    classroom = db.query(Classroom).filter(Classroom.id == assignment.classroom_id).first()
    if not classroom or classroom.teacher_id != user.id:
        raise HTTPException(status_code=403, detail="Only the teacher can delete this assignment")
    
    # Hard delete (submissions will be cascade deleted due to relationship)
    db.delete(assignment)
    db.commit()
    
    return None


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
    
    # 🔔 Notify student about grade
    try:
        comms = CommunicationService()
        student = db.query(User).filter(User.id == sub.student_id).first()
        
        if student:
            # Calculate percentage
            percentage = (payload.grade / assignment.max_points * 100) if assignment.max_points > 0 else 0
            grade_emoji = "🎉" if percentage >= 80 else "✅" if percentage >= 60 else "📊"
            
            comms.send_notification(
                user_id=student.id,
                message_type=MessageType.QUIZ_RESULT,
                priority=MessagePriority.MEDIUM,
                title=f"{grade_emoji} Assignment Graded: {classroom.name}",
                body=f"{assignment.title}: {payload.grade}/{assignment.max_points} ({percentage:.0f}%)",
                data={
                    "type": "assignment_graded",
                    "classroom_id": classroom.id,
                    "assignment_id": assignment.id,
                    "submission_id": sub.id,
                    "grade": payload.grade,
                    "max_points": assignment.max_points,
                    "percentage": percentage
                },
                user_phone=student.phone_number,
                user_email=student.email,
                has_app_installed=student.has_app_installed or False
            )
            
            logger.info(f"📊 Grade notification sent to student {student.id} for submission {sub.id}")
    except Exception as e:
        logger.error(f"❌ Failed to send grade notification: {e}")
        # Don't fail the request if notifications fail
    
    return {"detail": "graded", "id": sub.id}


@router.get("/student/grades")
async def student_grades(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    subs = db.query(Submission).filter(Submission.student_id == user.id, Submission.is_graded == 1).order_by(Submission.graded_at.desc()).all()
    return subs


# ---------------- AI Teacher Integration ----------------

class AskAIRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    context: Optional[str] = None


@router.post("/classrooms/{classroom_id}/ask-ai")
async def ask_ai_teacher(classroom_id: int, payload: AskAIRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Ask AI teacher a question in classroom context.
    
    AI has awareness of:
    - Classroom subject and grade level
    - Recent assignments and topics
    - Student's learning context
    """
    from app.services import ai_service
    
    # Verify user has access to classroom
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    is_teacher = classroom.teacher_id == user.id
    is_student = user in classroom.students
    
    if not (is_teacher or is_student):
        raise HTTPException(status_code=403, detail="Not a member of this classroom")
    
    if not ai_service.GEMINI_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI teacher is currently unavailable")
    
    # Build context-aware prompt
    classroom_context = f"""
You are an AI teaching assistant for {classroom.name}.
Subject: {classroom.subject or 'General'}
Grade Level: {classroom.grade_level or 'Not specified'}

Your role:
- Answer student questions clearly and pedagogically
- Relate answers to the classroom subject and level
- Encourage critical thinking
- Use examples appropriate for the grade level
"""
    
    # Get recent assignments for additional context
    recent_assignments = db.query(Assignment).filter(
        Assignment.classroom_id == classroom_id,
        Assignment.status == "published"
    ).order_by(Assignment.created_at.desc()).limit(3).all()
    
    if recent_assignments:
        assignment_topics = [a.title for a in recent_assignments]
        classroom_context += f"\n\nRecent topics covered: {', '.join(assignment_topics)}"
    
    if payload.context:
        classroom_context += f"\n\nAdditional context: {payload.context}"
    
    # Generate AI response
    try:
        full_prompt = f"{classroom_context}\n\nStudent Question: {payload.question}\n\nProvide a helpful, educational response:"
        response = ai_service.model.generate_content(full_prompt)
        
        logger.info(f"🤖 AI teacher answered question in classroom {classroom_id} for user {user.id}")
        
        return {
            "answer": response.text,
            "classroom_name": classroom.name,
            "subject": classroom.subject,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ AI teacher error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate response")
