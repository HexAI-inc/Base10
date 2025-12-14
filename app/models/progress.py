"""Progress tracking model for offline sync."""
from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime, String, Float, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Attempt(Base):
    """
    Student quiz attempts - the heart of offline sync.
    
    Sync Strategy:
    1. Student answers questions offline → stored in mobile SQLite
    2. Internet restored → POST /sync/push sends attempts to server
    3. Server saves to Postgres → calculates weak areas
    4. GET /sync/pull returns targeted questions
    
    device_id prevents duplicate syncs from same phone.
    """
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    
    # Attempt data
    is_correct = Column(Boolean, nullable=False)
    selected_option = Column(Integer, nullable=False)  # 0-3
    skipped = Column(Boolean, default=False)  # User skipped without answering
    
    # Spaced Repetition System (SM-2 Algorithm)
    srs_interval = Column(Integer, default=0)  # Days until next review
    srs_ease_factor = Column(Float, default=2.5)  # Difficulty multiplier (1.3-3.0)
    srs_repetitions = Column(Integer, default=0)  # Successful reviews in a row
    next_review_date = Column(DateTime(timezone=True), nullable=True)  # When to show again
    
    # Timing (crucial for analytics)
    attempted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Delta Sync Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete
    
    # Offline sync tracking
    device_id = Column(String, nullable=True)  # UUID from mobile device
    synced_at = Column(DateTime(timezone=True), nullable=True)  # When received by server
    
    # Relationships
    user = relationship("User", back_populates="attempts")
    question = relationship("Question", back_populates="attempts")
    
    # Composite index for fast lookups
    __table_args__ = (
        Index('idx_user_question', 'user_id', 'question_id'),
        Index('idx_user_date', 'user_id', 'attempted_at'),
        Index('idx_progress_updated_at', 'updated_at'),  # Critical for delta sync
        Index('idx_next_review', 'user_id', 'next_review_date'),  # SRS review queries
    )
    
    def __repr__(self):
        return f"<Attempt user={self.user_id} q={self.question_id} correct={self.is_correct}>"
