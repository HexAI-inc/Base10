"""Tests for scheduler.py's streak/notification wiring to real User fields.

scheduler.py manages its own DB sessions via app.db.session.SessionLocal
(it's a background job, not a request handler), independent of the
test_db/client fixtures used elsewhere - so these tests set up their own
tables on that same engine rather than going through conftest's fixtures.
"""
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models.user import User
from app.models.progress import Attempt
from app.models.enums import UserRole
from app.core.security import get_password_hash
from app.services import scheduler


@pytest.fixture
def scheduler_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def make_user(db, **overrides):
    defaults = dict(
        phone_number=f"+220{overrides.pop('suffix', '0000000')}",
        hashed_password=get_password_hash("testpass123"),
        full_name="Scheduler Test User",
        is_active=True,
        role=UserRole.STUDENT,
        study_streak=5,
        has_app_installed=False,
    )
    defaults.update(overrides)
    user = User(**defaults)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_streak_reset_for_inactive_user(scheduler_db):
    user = make_user(scheduler_db, suffix="1111111", study_streak=7, has_app_installed=True)

    with patch("app.services.scheduler.CommunicationService.send_notification") as mock_notify:
        scheduler.check_and_reset_streaks()

    scheduler_db.refresh(user)
    assert user.study_streak == 0

    mock_notify.assert_called_once()
    assert mock_notify.call_args.kwargs["has_app_installed"] is True


def test_streak_maintained_for_active_user(scheduler_db):
    user = make_user(scheduler_db, suffix="2222222", study_streak=3)

    yesterday = datetime.utcnow() - timedelta(days=1)
    attempt = Attempt(
        user_id=user.id,
        question_id=1,
        selected_option=0,
        is_correct=True,
        attempted_at=yesterday,
    )
    scheduler_db.add(attempt)
    scheduler_db.commit()

    with patch("app.services.scheduler.CommunicationService.send_notification") as mock_notify:
        scheduler.check_and_reset_streaks()

    scheduler_db.refresh(user)
    assert user.study_streak == 3  # untouched
    mock_notify.assert_not_called()


def test_review_reminder_reflects_real_app_installed_flag(scheduler_db):
    user = make_user(scheduler_db, suffix="3333333", has_app_installed=True)

    past_due = datetime.utcnow() - timedelta(days=1)
    for i in range(5):
        scheduler_db.add(Attempt(
            user_id=user.id,
            question_id=i + 1,
            selected_option=0,
            is_correct=True,
            attempted_at=datetime.utcnow(),
            next_review_date=past_due,
        ))
    scheduler_db.commit()

    with patch("app.services.scheduler.CommunicationService.send_notification") as mock_notify:
        scheduler.send_daily_review_reminders()

    mock_notify.assert_called_once()
    assert mock_notify.call_args.kwargs["has_app_installed"] is True
