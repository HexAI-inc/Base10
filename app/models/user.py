"""User model for authentication and progress tracking."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.enums import UserRole, GradeLevel


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
    username = Column(String(100), unique=True, index=True, nullable=True)  # Alternative login
    
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # For email/SMS verification
    is_onboarded = Column(Boolean, default=False)  # Whether they completed the setup wizard
    onboarding_step = Column(Integer, default=0)  # Current step in onboarding (0-3)
    verified_at = Column(DateTime(timezone=True), nullable=True)  # When verified
    
    # Email verification
    verification_token = Column(String(255), nullable=True)  # Secure token for email verification
    verification_token_expires = Column(DateTime(timezone=True), nullable=True)  # Token expiration (24 hours)
    
    # User role for onboarding flows
    role = Column(SQLEnum(UserRole), nullable=True, default=UserRole.STUDENT)
    
    # User profile & preferences (NEW: for content filtering)
    education_level = Column(SQLEnum(GradeLevel), nullable=True)  # "JSS1", "JSS3", "WASSCE", "GABECE"
    target_exam_date = Column(DateTime(timezone=True), nullable=True)  # When they're taking the exam
    preferred_subjects = Column(String(500), nullable=True)  # JSON array: ["Mathematics", "Physics"]
    
    # Extended profile fields
    avatar_url = Column(String(500), nullable=True)  # Profile photo URL
    bio = Column(String(500), nullable=True)  # About/bio section
    country = Column(String(100), nullable=True)  # Country code or name
    location = Column(String(200), nullable=True)  # City/region
    
    # Learning preferences
    learning_style = Column(String(50), nullable=True)  # "visual", "auditory", "kinesthetic", "reading_writing"
    study_time_preference = Column(String(50), nullable=True)  # "morning", "afternoon", "evening", "night"
    
    # Notification preferences (JSON)
    notification_settings = Column(String(1000), nullable=True)  # JSON: {"email": true, "sms": false, "push": true}
    
    # Privacy settings (JSON)
    privacy_settings = Column(String(1000), nullable=True)  # JSON: {"show_profile": true, "show_progress": false}
    
    # Gamification
    achievement_badges = Column(String(2000), nullable=True)  # JSON array of earned badges
    total_points = Column(Integer, default=0)  # Total gamification points
    level = Column(Integer, default=1)  # User level based on points
    
    # AI Quota Management
    ai_quota_limit = Column(Integer, default=100)  # Default 100 requests per month/period
    ai_quota_used = Column(Integer, default=0)  # Total requests used
    
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
