"""Tests for the classroom/recovery/moderation endpoints added while
reconciling the frontend against the backend (delete classroom, update/
delete assignment & material, list submissions, comment on stream post,
student message history, recovery verify-otp body fix, asset review)."""
from unittest.mock import patch, MagicMock

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.models.classroom import Classroom, Assignment, ClassroomMaterial, ClassroomPost, Submission, classroom_students
from app.models.user import User
from app.models.enums import UserRole
from app.models.asset import Asset
from app.core.security import get_password_hash, create_access_token


def make_classroom(db, teacher, **overrides):
    defaults = dict(name="Recon Test Class", teacher_id=teacher.id, join_code=overrides.pop("join_code", "RECON01"))
    defaults.update(overrides)
    classroom = Classroom(**defaults)
    db.add(classroom)
    db.commit()
    db.refresh(classroom)
    return classroom


@pytest.mark.asyncio
async def test_delete_classroom(client: AsyncClient, teacher_headers, test_teacher, session: Session):
    classroom = make_classroom(session, test_teacher, join_code="DEL0001")

    response = await client.delete(f"/api/v1/classrooms/{classroom.id}", headers=teacher_headers)
    assert response.status_code == 200
    assert session.query(Classroom).filter(Classroom.id == classroom.id).first() is None


@pytest.mark.asyncio
async def test_update_and_delete_assignment(client: AsyncClient, teacher_headers, test_teacher, session: Session):
    classroom = make_classroom(session, test_teacher, join_code="ASG0001")
    assignment = Assignment(classroom_id=classroom.id, title="Original Title", question_count=5)
    session.add(assignment)
    session.commit()
    session.refresh(assignment)

    update_response = await client.put(
        f"/api/v1/classrooms/assignments/{assignment.id}",
        json={"title": "Updated Title", "max_points": 50},
        headers=teacher_headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Title"

    delete_response = await client.delete(
        f"/api/v1/classrooms/assignments/{assignment.id}", headers=teacher_headers
    )
    assert delete_response.status_code == 200
    assert session.query(Assignment).filter(Assignment.id == assignment.id).first() is None


@pytest.mark.asyncio
async def test_update_and_delete_material(client: AsyncClient, teacher_headers, test_teacher, session: Session):
    classroom = make_classroom(session, test_teacher, join_code="MAT0001")
    material = ClassroomMaterial(classroom_id=classroom.id, uploaded_by_id=test_teacher.id, title="Old Title")
    session.add(material)
    session.commit()
    session.refresh(material)

    update_response = await client.put(
        f"/api/v1/classrooms/materials/{material.id}",
        json={"title": "New Title"},
        headers=teacher_headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "New Title"

    delete_response = await client.delete(
        f"/api/v1/classrooms/materials/{material.id}", headers=teacher_headers
    )
    assert delete_response.status_code == 200
    assert session.query(ClassroomMaterial).filter(ClassroomMaterial.id == material.id).first() is None


@pytest.mark.asyncio
async def test_list_submissions_and_grading_sets_is_graded(client: AsyncClient, teacher_headers, test_teacher, test_user, session: Session):
    classroom = make_classroom(session, test_teacher, join_code="SUB0001")
    assignment = Assignment(classroom_id=classroom.id, title="Essay", question_count=1)
    session.add(assignment)
    session.commit()
    session.refresh(assignment)

    submission = Submission(assignment_id=assignment.id, student_id=test_user.id, content_text="My answer")
    session.add(submission)
    session.commit()
    session.refresh(submission)

    grade_response = await client.post(
        f"/api/v1/classrooms/submissions/{submission.id}/grade",
        json={"grade": 88, "feedback": "Good work"},
        headers=teacher_headers,
    )
    assert grade_response.status_code == 200

    list_response = await client.get(
        f"/api/v1/classrooms/assignments/{assignment.id}/submissions", headers=teacher_headers
    )
    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data) == 1
    assert data[0]["grade"] == 88
    assert data[0]["is_graded"] is True  # regression check: used to stay False forever


@pytest.mark.asyncio
async def test_comment_on_stream_post(client: AsyncClient, teacher_headers, test_teacher, session: Session):
    classroom = make_classroom(session, test_teacher, join_code="CMT0001")
    post = ClassroomPost(classroom_id=classroom.id, author_id=test_teacher.id, content="Welcome!")
    session.add(post)
    session.commit()
    session.refresh(post)

    response = await client.post(
        f"/api/v1/classrooms/{classroom.id}/stream/{post.id}/comment",
        json={"content": "Nice post!"},
        headers=teacher_headers,
    )
    assert response.status_code == 201
    assert response.json()["parent_post_id"] == post.id


@pytest.mark.asyncio
async def test_get_student_messages(client: AsyncClient, teacher_headers, test_teacher, test_user, session: Session):
    classroom = make_classroom(session, test_teacher, join_code="MSG0001")
    session.execute(classroom_students.insert().values(classroom_id=classroom.id, student_id=test_user.id))
    session.commit()

    send_response = await client.post(
        f"/api/v1/classrooms/{classroom.id}/students/{test_user.id}/message",
        json={"message": "Keep up the good work!", "message_type": "encouragement"},
        headers=teacher_headers,
    )
    assert send_response.status_code == 200

    list_response = await client.get(
        f"/api/v1/classrooms/{classroom.id}/students/{test_user.id}/messages", headers=teacher_headers
    )
    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data) == 1
    assert data[0]["message"] == "Keep up the good work!"


@pytest.mark.asyncio
async def test_recovery_verify_otp_accepts_json_body(client: AsyncClient, test_db: Session):
    from app.models.otp import OTP
    from app.models.enums import OTPType
    from datetime import datetime, timedelta

    user = User(
        phone_number="+23276555000",
        hashed_password=get_password_hash("testpass123"),
        full_name="Recovery Test User",
        role=UserRole.STUDENT,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    otp = OTP(
        user_id=user.id,
        code="1234",
        purpose=OTPType.PHONE_VERIFY,
        expires_at=datetime.utcnow() + timedelta(minutes=15),
    )
    test_db.add(otp)
    test_db.commit()

    response = await client.post(
        "/api/v1/auth/verify-otp",
        json={"identifier": user.phone_number, "otp_code": "1234"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_review_asset(client: AsyncClient, test_db: Session):
    admin = User(
        phone_number="+23276555111",
        email="recon-admin@example.com",
        hashed_password=get_password_hash("adminpass123"),
        full_name="Recon Admin",
        role=UserRole.ADMIN,
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    admin_headers = {"Authorization": f"Bearer {create_access_token({'sub': str(admin.id)})}"}

    asset = Asset(filename="diagram.png", url="https://example.com/diagram.png", asset_type="image")
    test_db.add(asset)
    test_db.commit()
    test_db.refresh(asset)
    assert asset.status == "approved"  # default

    response = await client.post(
        f"/api/v1/moderation/assets/{asset.id}/review",
        json={"status": "rejected", "notes": "Low quality"},
        headers=admin_headers,
    )
    assert response.status_code == 200

    test_db.refresh(asset)
    assert asset.status == "rejected"
    assert asset.review_notes == "Low quality"
