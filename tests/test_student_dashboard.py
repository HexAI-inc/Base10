"""Tests for the student dashboard summary and answer submission flow.

Regression coverage for a real bug found while testing the frontend:
GET /student/dashboard/summary declared response_model=DashboardStats
(the full analytics schema, 7 extra required fields) but its handler
only ever returned the lightweight 7-field summary dict, so FastAPI's
response validation failed on every single call with a 500.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.models.question import Question


@pytest.fixture
def sample_question(test_db: Session):
    question = Question(
        subject="Mathematics",
        topic="Algebra",
        content="Solve for x: x + 1 = 2",
        options_json='["0", "1", "2", "3"]',
        correct_index=1,
        difficulty="easy",
    )
    test_db.add(question)
    test_db.commit()
    test_db.refresh(question)
    return question


@pytest.mark.asyncio
async def test_dashboard_summary_returns_200_for_new_user(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/student/dashboard/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    # Exactly the lightweight fields - not DashboardStats's full analytics shape
    assert set(data.keys()) == {
        "total_attempts", "overall_accuracy", "streak_days",
        "study_time_hours", "due_reviews", "today_attempts", "has_target_exam"
    }
    assert data["total_attempts"] == 0


@pytest.mark.asyncio
async def test_submit_answer_then_dashboard_summary_reflects_it(
    client: AsyncClient, auth_headers: dict, sample_question, test_db: Session
):
    submit_response = await client.post(
        "/api/v1/questions/submit",
        json={
            "question_id": sample_question.id,
            "selected_option": 1,
            "is_correct": True,
            "attempted_at": "2026-01-01T12:00:00",
            "time_taken_ms": 3000,
        },
        headers=auth_headers,
    )
    assert submit_response.status_code == 200

    summary_response = await client.get("/api/v1/student/dashboard/summary", headers=auth_headers)
    assert summary_response.status_code == 200
    data = summary_response.json()
    assert data["total_attempts"] == 1
    assert data["overall_accuracy"] == 100.0
