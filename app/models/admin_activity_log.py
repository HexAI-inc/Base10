"""Audit log of admin actions (deactivations, deletions, role changes, etc.)."""
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base


class AdminActivityLog(Base):
    """One recorded admin action, for the /admin/activity audit trail."""
    __tablename__ = "admin_activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    action_type = Column(String(50), nullable=False, index=True)  # e.g. "user.deactivate"
    action_description = Column(Text, nullable=False)

    target_type = Column(String(50), nullable=True)  # e.g. "user", "question"
    target_id = Column(Integer, nullable=True)

    metadata_json = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<AdminActivityLog admin={self.admin_id} action={self.action_type}>"
