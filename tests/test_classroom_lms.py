import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from app.models.classroom import Classroom, Assignment, ClassroomPost, ClassroomMaterial, Submission
from app.models.enums import UserRole, PostType
from app.core.security import create_access_token

@pytest.mark.asyncio
async def test_classroom_stream_lifecycle(client: AsyncClient, test_db: Session, test_teacher, test_user):
    """Test creating and retrieving stream posts."""
    # Create classroom
    classroom = Classroom(name="Stream Test", teacher_id=test_teacher.id, join_code="STREAM1")
    test_db.add(classroom)
    test_db.commit()
    test_db.refresh(classroom)

    teacher_token = create_access_token({"sub": str(test_teacher.id)})
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}

    # Create post
    response = await client.post(
        f"/api/v1/teacher/classrooms/{classroom.id}/stream",
        json={"content": "Welcome to the class!", "post_type": "announcement"},
        headers=teacher_headers
    )
    assert response.status_code == 201
    post_id = response.json()["id"]

    # Get stream
    response = await client.get(
        f"/api/v1/teacher/classrooms/{classroom.id}/stream",
        headers=teacher_headers
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["content"] == "Welcome to the class!"

@pytest.mark.asyncio
async def test_classroom_materials(client: AsyncClient, test_db: Session, test_teacher):
    """Test adding and listing materials."""
    classroom = Classroom(name="Material Test", teacher_id=test_teacher.id, join_code="MAT1")
    test_db.add(classroom)
    test_db.commit()
    test_db.refresh(classroom)

    teacher_token = create_access_token({"sub": str(test_teacher.id)})
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}

    # 2. Add material
    response = await client.post(
        f"/api/v1/teacher/classrooms/{classroom.id}/materials",
        json={"title": "Syllabus", "description": "Course overview"},
        headers=teacher_headers
    )
    if response.status_code != 201:
        print(f"Material creation failed: {response.json()}")
    assert response.status_code == 201

    # List materials
    response = await client.get(
        f"/api/v1/teacher/classrooms/{classroom.id}/materials",
        headers=teacher_headers
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Syllabus"

@pytest.mark.asyncio
async def test_assignment_submission_flow(client: AsyncClient, test_db: Session, test_teacher, test_user):
    """Test the full flow of assignment creation, submission, and grading."""
    # 1. Setup Classroom and Student
    classroom = Classroom(name="LMS Flow Test", teacher_id=test_teacher.id, join_code="FLOW1")
    test_db.add(classroom)
    test_db.commit()
    
    # Student joins
    from app.models.classroom import classroom_students
    test_db.execute(classroom_students.insert().values(classroom_id=classroom.id, student_id=test_user.id))
    test_db.commit()

    teacher_token = create_access_token({"sub": str(test_teacher.id)})
    student_token = create_access_token({"sub": str(test_user.id)})
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
    student_headers = {"Authorization": f"Bearer {student_token}"}

    # 2. Teacher creates assignment
    response = await client.post(
        f"/api/v1/teacher/classrooms/{classroom.id}/assignments",
        json={
            "classroom_id": classroom.id,
            "title": "Final Project",
            "description": "Submit your work here",
            "question_count": 10
        },
        headers=teacher_headers
    )
    assert response.status_code == 201
    assignment_id = response.json()["id"]

    # 3. Student submits assignment
    response = await client.post(
        f"/api/v1/teacher/classrooms/assignments/{assignment_id}/submit",
        json={"content_text": "My project work..."},
        headers=student_headers
    )
    assert response.status_code == 201
    submission_id = response.json()["submission_id"]

    # 4. Teacher grades submission
    response = await client.post(
        f"/api/v1/teacher/classrooms/submissions/{submission_id}/grade",
        json={"grade": 95, "feedback": "Excellent work!"},
        headers=teacher_headers
    )
    assert response.status_code == 200
