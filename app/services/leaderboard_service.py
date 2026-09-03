"""Shared leaderboard computation, used by both the scheduler's cache-warming
job and the API's on-demand fallback when the cache is empty (e.g. before
the job has ever run, or if Redis is unavailable)."""
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy import func, Integer
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.progress import Attempt


def compute_leaderboard(db: Session, days: int, limit: int = 100) -> List[Dict[str, Any]]:
    """Rank users by attempts (then accuracy) over the last `days` days."""
    window_start = datetime.utcnow() - timedelta(days=days)

    rows = db.query(
        User.id,
        User.full_name,
        func.count(Attempt.id).label('attempts'),
        (func.sum(func.cast(Attempt.is_correct, Integer)) * 100.0 /
         func.count(Attempt.id)).label('accuracy')
    ).join(
        Attempt, Attempt.user_id == User.id
    ).filter(
        Attempt.attempted_at >= window_start
    ).group_by(
        User.id, User.full_name
    ).order_by(
        func.count(Attempt.id).desc(),
        (func.sum(func.cast(Attempt.is_correct, Integer)) * 100.0 /
         func.count(Attempt.id)).desc()
    ).limit(limit).all()

    return [
        {
            'rank': idx + 1,
            'user_id': user.id,
            'name': user.full_name or 'Anonymous',
            'attempts': user.attempts,
            'accuracy': round(user.accuracy, 2),
        }
        for idx, user in enumerate(rows)
    ]
