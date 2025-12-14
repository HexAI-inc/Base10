"""User model for authentication and progress tracking."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class User(Base):
    """
    User model supporting both SMS and Web/Mobile authentication.
    
    Critical for rural students: 
    - phone_number for SMS-only users (no data plan needed)
    - email for web/app users
    - At least ONE must be provided
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multiple auth methods for low-connectivity environments
    phone_number = Column(String, unique=True, index=True, nullable=True)  # +2207777777 format
    email = Column(String, unique=True, index=True, nullable=True)
    
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # For SMS verification
    
    # User profile & preferences (NEW: for content filtering)
    education_level = Column(String(50), nullable=True)  # "JSS1", "JSS3", "WASSCE", "GABECE"
    target_exam_date = Column(DateTime(timezone=True), nullable=True)  # When they're taking the exam
    preferred_subjects = Column(String(500), nullable=True)  # JSON array: ["Mathematics", "Physics"]
    
    # Engagement tracking
    has_app_installed = Column(Boolean, default=False)  # For smart notification routing
    study_streak = Column(Integer, default=0)  # Consecutive days with activity
    last_activity_date = Column(DateTime(timezone=True), nullable=True)  # For streak calculation
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete for delta sync
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    attempts = relationship("Attempt", back_populates="user")
    otps = relationship("OTP", back_populates="user")
    reports_submitted = relationship("QuestionReport", foreign_keys="QuestionReport.user_id", back_populates="reporter")
    flashcard_progress = relationship("FlashcardReview", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.phone_number or self.email}>"
