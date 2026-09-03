"""Helper for recording admin actions to the audit trail."""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.admin_activity_log import AdminActivityLog


def log_admin_action(
    db: Session,
    admin_id: int,
    action_type: str,
    action_description: str,
    target_type: Optional[str] = None,
    target_id: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> AdminActivityLog:
    """
    Record an admin action. Added to the session but not committed -
    callers should let their existing db.commit() cover this alongside
    the actual mutation, so the log and the change land atomically.
    """
    entry = AdminActivityLog(
        admin_id=admin_id,
        action_type=action_type,
        action_description=action_description,
        target_type=target_type,
        target_id=target_id,
        metadata_json=metadata
    )
    db.add(entry)
    return entry
