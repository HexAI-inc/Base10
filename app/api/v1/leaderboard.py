"""
Leaderboard API - Weekly/Monthly Rankings.

Serves cached leaderboard data from Redis for fast response times.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.redis_client import redis_client
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


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
    current_user: User = Depends(get_current_user)
):
    """
    Get weekly leaderboard (top 100 users).
    
    Updated every Sunday at 23:00 GMT by scheduler.
    Cached in Redis for fast response.
    """
    # Try to get from cache
    cached_data = redis_client.get_leaderboard(period="weekly")
    
    if not cached_data:
        raise HTTPException(
            status_code=503,
            detail="Leaderboard data not available yet. Check back soon!"
        )
    
    # Find current user's rank
    user_rank = None
    for entry in cached_data:
        if entry['user_id'] == current_user.id:
            user_rank = entry['rank']
            break
    
    return LeaderboardResponse(
        period="weekly",
        updated_at=datetime.utcnow(),  # TODO: Store actual update timestamp
        leaderboard=[LeaderboardEntry(**entry) for entry in cached_data],
        user_rank=user_rank
    )


@router.get("/monthly", response_model=LeaderboardResponse)
def get_monthly_leaderboard(
    current_user: User = Depends(get_current_user)
):
    """
    Get monthly leaderboard (top 100 users).
    
    Updated on 1st of each month by scheduler.
    """
    cached_data = redis_client.get_leaderboard(period="monthly")
    
    if not cached_data:
        raise HTTPException(
            status_code=503,
            detail="Monthly leaderboard not available yet."
        )
    
    # Find current user's rank
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
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's rank in weekly and monthly leaderboards.
    
    Quick lookup without fetching full leaderboard.
    """
    weekly_data = redis_client.get_leaderboard(period="weekly")
    monthly_data = redis_client.get_leaderboard(period="monthly")
    
    weekly_rank = None
    monthly_rank = None
    
    if weekly_data:
        for entry in weekly_data:
            if entry['user_id'] == current_user.id:
                weekly_rank = entry['rank']
                break
    
    if monthly_data:
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
