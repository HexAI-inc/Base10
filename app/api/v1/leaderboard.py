"""
Leaderboard API - Weekly/Monthly Rankings.

Serves cached leaderboard data from Redis for fast response times.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.redis_client import redis_client
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.leaderboard_service import compute_leaderboard

router = APIRouter()

_PERIOD_DAYS = {"weekly": 7, "monthly": 30}


def _get_leaderboard_data(db: Session, period: str) -> list:
    """Cached leaderboard if the scheduler has warmed it, otherwise compute
    on demand - keeps this endpoint usable before the weekly job has ever
    run, or if Redis is unavailable, rather than a hard 503."""
    cached_data = redis_client.get_leaderboard(period=period)
    if cached_data:
        return cached_data

    computed = compute_leaderboard(db, days=_PERIOD_DAYS[period], limit=100)
    redis_client.set_leaderboard(computed, period=period, ttl=3600)
    return computed


class LeaderboardEntry(BaseModel):
    """Leaderboard entry schema."""
    rank: int
    user_id: int
    name: str
    attempts: int
    accuracy: float


class LeaderboardResponse(BaseModel):
    """Leaderboard API response."""
    period: str  # 'weekly' or 'monthly'
    updated_at: Optional[datetime]
    leaderboard: List[LeaderboardEntry]
    user_rank: Optional[int] = None  # Current user's rank


@router.get("/weekly", response_model=LeaderboardResponse)
def get_weekly_leaderboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get weekly leaderboard (top 100 users, last 7 days of activity).

    Served from the Redis cache the scheduler warms every Sunday;
    computed on demand if that cache is empty (first run, cache expiry,
    or Redis unavailable) rather than erroring.
    """
    cached_data = _get_leaderboard_data(db, "weekly")

    user_rank = None
    for entry in cached_data:
        if entry['user_id'] == current_user.id:
            user_rank = entry['rank']
            break

    return LeaderboardResponse(
        period="weekly",
        updated_at=datetime.utcnow(),
        leaderboard=[LeaderboardEntry(**entry) for entry in cached_data],
        user_rank=user_rank
    )


@router.get("/monthly", response_model=LeaderboardResponse)
def get_monthly_leaderboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get monthly leaderboard (top 100 users, last 30 days of activity).

    Served from cache if warmed; computed on demand otherwise.
    """
    cached_data = _get_leaderboard_data(db, "monthly")

    user_rank = None
    for entry in cached_data:
        if entry['user_id'] == current_user.id:
            user_rank = entry['rank']
            break

    return LeaderboardResponse(
        period="monthly",
        updated_at=datetime.utcnow(),
        leaderboard=[LeaderboardEntry(**entry) for entry in cached_data],
        user_rank=user_rank
    )


@router.get("/my-rank")
def get_my_rank(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's rank in weekly and monthly leaderboards.

    Quick lookup without fetching full leaderboard.
    """
    weekly_data = _get_leaderboard_data(db, "weekly")
    monthly_data = _get_leaderboard_data(db, "monthly")

    weekly_rank = None
    monthly_rank = None

    for entry in weekly_data:
        if entry['user_id'] == current_user.id:
            weekly_rank = entry['rank']
            break

    for entry in monthly_data:
        if entry['user_id'] == current_user.id:
            monthly_rank = entry['rank']
            break

    return {
        "user_id": current_user.id,
        "name": current_user.full_name,
        "weekly_rank": weekly_rank,
        "monthly_rank": monthly_rank,
        "message": "Keep studying to climb the ranks! 🚀" if weekly_rank and weekly_rank > 10 else "You're doing great! 🌟"
    }
