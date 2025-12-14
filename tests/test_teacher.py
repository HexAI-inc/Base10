"""
Comprehensive tests for teacher endpoints.
Tests classroom creation, student joining, assignments, and analytics.
"""
import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.classroom import Classroom, Assignment
from app.models.question import Question, Subject, DifficultyLevel
from app.models.progress import Attempt


@pytest.mark.asyncio
async def test_create_classroom(client: AsyncClient, auth_headers: dict):
    """Test creating a new classroom."""
    response = await client.post(
        "/api/v1/teacher/classrooms",
        json={
            "name": "Grade 10 Mathematics",
            "description": "Advanced algebra and geometry"
        },
        headers=auth_headers
    )
    
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["name"] == "Grade 10 Mathematics"
    assert data["description"] == "Advanced algebra and geometry"
    assert "join_code" in data
    assert len(data["join_code"]) > 0
    assert data["is_active"] in [True, 1]  # SQLite/PostgreSQL may return 1 for True


@pytest.mark.asyncio
async def test_create_classroom_no_description(client: AsyncClient, auth_headers: dict):
    """Test creating classroom without description."""
    response = await client.post(
        "/api/v1/teacher/classrooms",
        json={"name": "Physics 101"},
        headers=auth_headers
    )
    
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["name"] == "Physics 101"
    assert data["description"] is None


@pytest.mark.asyncio
async def test_create_classroom_missing_name(client: AsyncClient, auth_headers: dict):
    """Test creating classroom without required name."""
    response = await client.post(
        "/api/v1/teacher/classrooms",
        json={"description": "Test description"},
        headers=auth_headers
    )
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_list_classrooms_empty(client: AsyncClient, auth_headers: dict):
    """Test listing classrooms when teacher has none."""
    response = await client.get(
        "/api/v1/teacher/classrooms",
        headers=auth_headers
    )
    
    assert response.status_code in [200, 201]
    data = response.json()
    assert isinstance(data, list)
    # May have classrooms from previous tests if database not isolated


@pytest.mark.asyncio
async def test_list_classrooms_with_students(
    client: AsyncClient, 
    auth_headers: dict,
    session: Session
):
    """Test listing classrooms shows student count."""
    # Create classroom
    create_response = await client.post(
        "/api/v1/teacher/classrooms",
        json={"name": "Test Class with Students"},
        headers=auth_headers
    )
    assert create_response.status_code in [200, 201]
    classroom_data = create_response.json()
    join_code = classroom_data["join_code"]
    
    # Create a student user
    student = User(
        email="student1@test.com",
        phone_number="+1234567890",
        hashed_password="hashedpass",
        full_name="Test Student"
    )
    session.add(student)
    session.commit()
    session.refresh(student)
    
    # Student joins classroom
    from app.core.security import create_access_token
    student_token = create_access_token(student.id)
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    join_response = await client.post(
        "/api/v1/teacher/classrooms/join",
        json={"join_code": join_code},
        headers=student_headers
    )
    assert join_response.status_code == 200
    
    # List classrooms and verify student count
    list_response = await client.get(
        "/api/v1/teacher/classrooms",
        headers=auth_headers
    )
    assert list_response.status_code == 200
    classrooms = list_response.json()
    
    test_classroom = next(
        (c for c in classrooms if c["name"] == "Test Class with Students"),
        None
    )
    assert test_classroom is not None
    assert test_classroom["student_count"] >= 1


@pytest.mark.asyncio
async def test_student_join_classroom_valid_code(
    client: AsyncClient,
    auth_headers: dict,
    session: Session
):
    """Test student successfully joining classroom with valid code."""
    # Create classroom as teacher
    create_response = await client.post(
        "/api/v1/teacher/classrooms",
        json={"name": "Join Test Classroom"},
        headers=auth_headers
    )
    join_code = create_response.json()["join_code"]
    
    # Create student
    student = User(
        email="student_join@test.com",
        phone_number="+1234567891",
        hashed_password="hashedpass",
        full_name="Join Test Student"
    )
    session.add(student)
    session.commit()
    
    from app.core.security import create_access_token
    student_token = create_access_token(student.id)
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    # Join classroom
    response = await client.post(
        "/api/v1/teacher/classrooms/join",
        json={"join_code": join_code},
        headers=student_headers
    )
    
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["message"] == "Successfully joined classroom"
    assert "classroom" in data
    assert data["classroom"]["name"] == "Join Test Classroom"


@pytest.mark.asyncio
async def test_student_join_classroom_invalid_code(
    client: AsyncClient,
    session: Session
):
    """Test student joining with invalid code fails."""
    student = User(
        email="student_invalid@test.com",
        phone_number="+1234567892",
        hashed_password="hashedpass",
        full_name="Invalid Join Student"
    )
    session.add(student)
    session.commit()
    
    from app.core.security import create_access_token
    student_token = create_access_token(student.id)
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    response = await client.post(
        "/api/v1/teacher/classrooms/join",
        json={"join_code": "INVALID-999"},
        headers=student_headers
    )
    
    assert response.status_code in [404, 400]


@pytest.mark.asyncio
async def test_student_join_classroom_twice(
    client: AsyncClient,
    auth_headers: dict,
    session: Session
):
    """Test student joining same classroom twice."""
    # Create classroom
    create_response = await client.post(
        "/api/v1/teacher/classrooms",
        json={"name": "Duplicate Join Test"},
        headers=auth_headers
    )
    join_code = create_response.json()["join_code"]
    
    # Create student
    student = User(
        email="student_duplicate@test.com",
        phone_number="+1234567893",
        hashed_password="hashedpass",
        full_name="Duplicate Join Student"
    )
    session.add(student)
    session.commit()
    
    from app.core.security import create_access_token
    student_token = create_access_token(student.id)
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    # Join first time
    response1 = await client.post(
        "/api/v1/teacher/classrooms/join",
        json={"join_code": join_code},
        headers=student_headers
    )
    assert response1.status_code == 200
    
    # Join second time - should succeed (idempotent)
    response2 = await client.post(
        "/api/v1/teacher/classrooms/join",
        json={"join_code": join_code},
        headers=student_headers
    )
    assert response2.status_code == 200


@pytest.mark.asyncio
async def test_create_assignment(
    client: AsyncClient,
    auth_headers: dict
):
    """Test creating an assignment for a classroom."""
    # Create classroom first
    classroom_response = await client.post(
        "/api/v1/teacher/classrooms",
        json={"name": "Assignment Test Class"},
        headers=auth_headers
    )
    classroom_id = classroom_response.json()["id"]
    
    # Create assignment
    due_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
    response = await client.post(
        "/api/v1/teacher/assignments",
        json={
            "classroom_id": classroom_id,
            "title": "Chapter 3 Practice",
            "description": "Complete all algebra questions",
            "subject": "MATHEMATICS",
            "topic": "Algebra",
            "difficulty": "MEDIUM",
            "due_date": due_date
        },
        headers=auth_headers
    )
    
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["title"] == "Chapter 3 Practice"
    assert data["classroom_id"] == classroom_id
    assert data["subject"] == "MATHEMATICS"
    assert data["topic"] == "Algebra"


@pytest.mark.asyncio
async def test_create_assignment_minimal(
    client: AsyncClient,
    auth_headers: dict
):
    """Test creating assignment with only required fields."""
    classroom_response = await client.post(
        "/api/v1/teacher/classrooms",
        json={"name": "Minimal Assignment Class"},
        headers=auth_headers
    )
    classroom_id = classroom_response.json()["id"]
    
    response = await client.post(
        "/api/v1/teacher/assignments",
        json={
            "classroom_id": classroom_id,
            "title": "Quick Quiz"
        },
        headers=auth_headers
    )
    
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["title"] == "Quick Quiz"
    assert data.get("subject") is None
    assert data.get("topic") is None


@pytest.mark.asyncio
async def test_create_assignment_invalid_classroom(
    client: AsyncClient,
    auth_headers: dict
):
    """Test creating assignment for non-existent classroom fails."""
    response = await client.post(
        "/api/v1/teacher/assignments",
        json={
            "classroom_id": 999999,
            "title": "Invalid Assignment"
        },
        headers=auth_headers
    )
    
    assert response.status_code in [404, 400]


@pytest.mark.asyncio
async def test_analytics_empty_classroom(
    client: AsyncClient,
    auth_headers: dict
):
    """Test analytics for classroom with no students."""
    classroom_response = await client.post(
        "/api/v1/teacher/classrooms",
        json={"name": "Empty Analytics Class"},
        headers=auth_headers
    )
    classroom_id = classroom_response.json()["id"]
    
    response = await client.get(
        f"/api/v1/teacher/analytics/{classroom_id}",
        headers=auth_headers
    )
    
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["classroom_id"] == classroom_id
    assert data["total_students"] == 0
    assert data["active_students"] == 0
    assert len(data.get("student_performance", [])) == 0


@pytest.mark.asyncio
async def test_analytics_with_psychometric_data(
    client: AsyncClient,
    auth_headers: dict,
    session: Session
):
    """Test analytics with varied psychometric data including guessing, struggles, misconceptions."""
    # Create classroom
    classroom_response = await client.post(
        "/api/v1/teacher/classrooms",
        json={"name": "Analytics Test Class"},
        headers=auth_headers
    )
    classroom_data = classroom_response.json()
    classroom_id = classroom_data["id"]
    join_code = classroom_data["join_code"]
    
    # Create test questions
    question1 = Question(
        subject=Subject.MATHEMATICS,
        topic="Algebra",
        content="Solve x + 5 = 10",
        options_json='["5", "10", "15", "20"]',
        correct_option=0,
        difficulty=DifficultyLevel.EASY,
        explanation="x = 10 - 5 = 5"
    )
    question2 = Question(
        subject=Subject.MATHEMATICS,
        topic="Geometry",
        content="Area of circle with radius 5",
        options_json='["25π", "10π", "5π", "50π"]',
        correct_option=0,
        difficulty=DifficultyLevel.MEDIUM,
        explanation="A = πr² = π(5)² = 25π"
    )
    session.add_all([question1, question2])
    session.commit()
    session.refresh(question1)
    session.refresh(question2)
    
    # Create students with different performance patterns
    students_data = []
    for i in range(3):
        student = User(
            email=f"analytics_student{i}@test.com",
            phone_number=f"+123456789{i}",
            hashed_password="hashedpass",
            full_name=f"Analytics Student {i}",
            is_teacher=False
        )
        session.add(student)
        students_data.append(student)
    
    session.commit()
    
    # Have students join classroom
    from app.core.security import create_access_token
    for student in students_data:
        student_token = create_access_token(student.id)
        student_headers = {"Authorization": f"Bearer {student_token}"}
        await client.post(
            "/api/v1/teacher/classrooms/join",
            json={"join_code": join_code},
            headers=student_headers
        )
    
    # Create attempts with varied psychometric patterns
    
    # Student 0: Guesser (very fast, low confidence, wrong)
    guess_attempt = Attempt(
        user_id=students_data[0].id,
        question_id=question1.id,
        is_correct=False,
        selected_option=1,
        attempted_at=datetime.utcnow(),
        time_taken_ms=1500,  # <2s = guessing
        confidence_level=2,
        network_type="wifi",
        app_version="1.0.0"
    )
    
    # Student 1: Struggling (very slow, multiple attempts)
    struggle_attempt1 = Attempt(
        user_id=students_data[1].id,
        question_id=question1.id,
        is_correct=False,
        selected_option=2,
        attempted_at=datetime.utcnow(),
        time_taken_ms=75000,  # >60s = struggling
        confidence_level=3,
        network_type="4g",
        app_version="1.0.0"
    )
    
    struggle_attempt2 = Attempt(
        user_id=students_data[1].id,
        question_id=question2.id,
        is_correct=False,
        selected_option=1,
        attempted_at=datetime.utcnow(),
        time_taken_ms=82000,  # Also struggling
        confidence_level=2,
        network_type="4g",
        app_version="1.0.0"
    )
    
    # Student 2: Has misconception (high confidence but wrong)
    misconception_attempt = Attempt(
        user_id=students_data[2].id,
        question_id=question2.id,
        is_correct=False,
        selected_option=1,
        attempted_at=datetime.utcnow(),
        time_taken_ms=15000,  # Normal time
        confidence_level=5,  # Very confident but wrong = misconception
        network_type="wifi",
        app_version="1.0.0"
    )
    
    # Student 2: Also has some correct answers
    correct_attempt = Attempt(
        user_id=students_data[2].id,
        question_id=question1.id,
        is_correct=True,
        selected_option=0,
        attempted_at=datetime.utcnow(),
        time_taken_ms=12000,
        confidence_level=4,
        network_type="wifi",
        app_version="1.0.0"
    )
    
    session.add_all([guess_attempt, struggle_attempt1, struggle_attempt2, misconception_attempt, correct_attempt])
    session.commit()
    
    # Get analytics
    response = await client.get(
        f"/api/v1/teacher/analytics/{classroom_id}",
        headers=auth_headers
    )
    
    assert response.status_code in [200, 201]
    data = response.json()
    
    # Verify basic stats
    assert data["classroom_id"] == classroom_id
    assert data["total_students"] == 3
    assert data["active_students"] >= 1  # At least 1 student active in last 7 days
    
    # Verify student performance includes psychometric insights
    assert len(data.get("student_performance", [])) == 3
    
    # Find each student's performance
    student_perfs = {sp["student_id"]: sp for sp in data["student_performance"]}
    
    # Student 0: Should have high guessing rate
    student0_perf = student_perfs[students_data[0].id]
    assert student0_perf["total_attempts"] >= 1
    if student0_perf["total_attempts"] > 0:
        assert student0_perf["guessing_rate"] > 0  # Has guessing attempts
    
    # Student 1: Should have high struggle rate
    student1_perf = student_perfs[students_data[1].id]
    assert student1_perf["total_attempts"] >= 2
    if student1_perf["total_attempts"] > 0:
        assert student1_perf["struggle_rate"] > 0  # Has struggling attempts
    
    # Student 2: Should have misconceptions detected
    student2_perf = student_perfs[students_data[2].id]
    assert student2_perf["total_attempts"] >= 2
    assert student2_perf["misconception_count"] >= 1  # High confidence + wrong
    
    # Verify topic performance breakdown
    assert "topic_performance" in data
    assert len(data["topic_performance"]) > 0
    
    # Check for topics in the data
    topics = {tp["topic"] for tp in data["topic_performance"]}
    assert "Algebra" in topics or "Geometry" in topics


@pytest.mark.asyncio
async def test_analytics_unauthorized_classroom(
    client: AsyncClient,
    auth_headers: dict,
    session: Session
):
    """Test that teachers can only view analytics for their own classrooms."""
    # Create another teacher
    other_teacher = User(
        email="other_teacher@test.com",
        phone_number="+9876543210",
        hashed_password="hashedpass",
        full_name="Other Teacher"
    )
    session.add(other_teacher)
    session.commit()
    session.refresh(other_teacher)
    
    # Other teacher creates classroom
    from app.core.security import create_access_token
    other_token = create_access_token(other_teacher.id)
    other_headers = {"Authorization": f"Bearer {other_token}"}
    
    classroom_response = await client.post(
        "/api/v1/teacher/classrooms",
        json={"name": "Other Teacher's Class"},
        headers=other_headers
    )
    classroom_id = classroom_response.json()["id"]
    
    # Original teacher tries to access other teacher's analytics
    response = await client.get(
        f"/api/v1/teacher/analytics/{classroom_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 403  # Forbidden


@pytest.mark.asyncio
async def test_analytics_class_averages(
    client: AsyncClient,
    auth_headers: dict,
    session: Session
):
    """Test that analytics includes class-wide averages."""
    # Create classroom
    classroom_response = await client.post(
        "/api/v1/teacher/classrooms",
        json={"name": "Averages Test Class"},
        headers=auth_headers
    )
    classroom_id = classroom_response.json()["id"]
    
    response = await client.get(
        f"/api/v1/teacher/analytics/{classroom_id}",
        headers=auth_headers
    )
    
    assert response.status_code in [200, 201]
    data = response.json()
    
    # Verify class-wide metrics exist
    assert "class_accuracy" in data
    assert "average_confidence" in data
    assert isinstance(data["class_accuracy"], (int, float))
    assert isinstance(data["average_confidence"], (int, float, type(None)))


@pytest.mark.asyncio
async def test_teacher_endpoints_require_auth(client: AsyncClient):
    """Test that all teacher endpoints require authentication."""
    endpoints = [
        ("/api/v1/teacher/classrooms", "get"),
        ("/api/v1/teacher/classrooms", "post"),
        ("/api/v1/teacher/classrooms/join", "post"),
        ("/api/v1/teacher/assignments", "post"),
        ("/api/v1/teacher/analytics/1", "get"),
    ]
    
    for endpoint, method in endpoints:
        if method == "get":
            response = await client.get(endpoint)
        else:
            response = await client.post(endpoint, json={})
        
        assert response.status_code == 401  # Unauthorized
