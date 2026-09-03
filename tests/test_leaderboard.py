"""Tests for the leaderboard on-demand computation fallback.

Regression coverage for two real bugs found while closing out the
frontend work: scheduler.calculate_weekly_leaderboard() crashed every
time it ran (func.cast(..., db.Integer) - db is a Session, not the
sqlalchemy module, so it has no .Integer), and there was no monthly
leaderboard job at all - meaning /leaderboard/weekly and
/leaderboard/monthly were both permanently stuck returning 503 in any
real deployment, cache warm-up or not.
"""
from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.models.question import Question
from app.models.progress import Attempt
from app.services.leaderboard_service import compute_leaderboard


@pytest.fixture
def attempts_for_user(test_db: Session, test_user):
    question = Question(
        subject="Mathematics", topic="Algebra", content="2+2?",
        options_json='["3","4","5","6"]', correct_index=1, difficulty="easy",
    )
    test_db.add(question)
    test_db.commit()
    test_db.refresh(question)

    for i in range(3):
        test_db.add(Attempt(
            user_id=test_user.id,
            question_id=question.id,
            selected_option=1,
            is_correct=True,
            attempted_at=datetime.utcnow() - timedelta(days=i),
        ))
    test_db.commit()
    return question


def test_compute_leaderboard_does_not_crash(test_db: Session, attempts_for_user):
    """The actual bug: func.cast(..., db.Integer) raised AttributeError."""
    result = compute_leaderboard(test_db, days=7, limit=100)
    assert len(result) == 1
    assert result[0]["attempts"] == 3
    assert result[0]["accuracy"] == 100.0
    assert result[0]["rank"] == 1


def test_compute_leaderboard_respects_time_window(test_db: Session, test_user):
    question = Question(
        subject="Mathematics", topic="Algebra", content="1+1?",
        options_json='["1","2","3","4"]', correct_index=1, difficulty="easy",
    )
    test_db.add(question)
    test_db.commit()
    test_db.refresh(question)

    test_db.add(Attempt(
        user_id=test_user.id, question_id=question.id,
        selected_option=1, is_correct=True,
        attempted_at=datetime.utcnow() - timedelta(days=20),
    ))
    test_db.commit()

    weekly = compute_leaderboard(test_db, days=7, limit=100)
    monthly = compute_leaderboard(test_db, days=30, limit=100)
    assert len(weekly) == 0  # outside the 7-day window
    assert len(monthly) == 1  # inside the 30-day window


@pytest.mark.asyncio
async def test_weekly_leaderboard_endpoint_computes_on_demand(
    client: AsyncClient, auth_headers: dict, attempts_for_user
):
    """No cache warm-up (no Redis, no scheduler run) - should still return
    real data instead of the old hard 503."""
    response = await client.get("/api/v1/leaderboard/weekly", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["period"] == "weekly"
    assert len(data["leaderboard"]) == 1
    assert data["user_rank"] == 1


@pytest.mark.asyncio
async def test_monthly_leaderboard_endpoint_computes_on_demand(
    client: AsyncClient, auth_headers: dict, attempts_for_user
):
    response = await client.get("/api/v1/leaderboard/monthly", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["period"] == "monthly"


@pytest.mark.asyncio
async def test_my_rank_endpoint(client: AsyncClient, auth_headers: dict, attempts_for_user):
    response = await client.get("/api/v1/leaderboard/my-rank", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["weekly_rank"] == 1
    assert data["monthly_rank"] == 1
