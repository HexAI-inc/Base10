"""Content feedback model for crowdsourced quality control."""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum as SQLEnum, func, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.enums import ReportStatus, ReportReason


class QuestionReport(Base):

    """
    User-submitted reports for question quality issues.
    
    Design:
    - Crowdsourced QA from students in the field
    - Admin dashboard can prioritize by report_count
    - Tracks user reputation (prevents spam)
    """
    __tablename__ = "question_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # What was reported
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Report details
    reason = Column(SQLEnum(ReportReason), nullable=False)
    comment = Column(Text, nullable=True)  # Optional explanation
    
    # Admin moderation
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.PENDING)
    admin_notes = Column(Text, nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    question = relationship("Question", back_populates="reports")
    reporter = relationship("User", foreign_keys=[user_id], back_populates="reports_submitted")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    
    def __repr__(self):
        return f"<Report Q{self.question_id} by U{self.user_id}: {self.reason.value}>"
