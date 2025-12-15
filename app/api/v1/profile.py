"""User profile and preferences management."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from app.db.session import get_db
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter()


def _calculate_profile_completion(user: User) -> int:
    """Calculate profile completion percentage."""
    fields = [
        user.full_name,
        user.email or user.phone_number,
        user.education_level,
        user.target_exam_date,
        user.preferred_subjects,
        user.avatar_url,
        user.bio,
        user.country,
        user.learning_style,
        user.notification_settings,
        user.privacy_settings
    ]
    
    filled = sum(1 for field in fields if field)
    return int((filled / len(fields)) * 100)


class LearningStyle(str, Enum):
    """Learning style preferences."""
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"


class StudyTimePreference(str, Enum):
    """Preferred study time."""
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"


class NotificationSettings(BaseModel):
    """Notification preferences."""
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = True
    daily_reminder: bool = True
    weekly_progress: bool = True
    exam_countdown: bool = True
    achievement_alerts: bool = True


class PrivacySettings(BaseModel):
    """Privacy preferences."""
    show_profile: bool = True
    show_progress: bool = True
    show_in_leaderboard: bool = True
    allow_classmate_comparison: bool = True


class ProfileUpdateRequest(BaseModel):
    """User profile update schema."""
    full_name: Optional[str] = None
    education_level: Optional[str] = None  # "JSS1", "JSS2", "JSS3", "WASSCE", "GABECE"
    target_exam_date: Optional[str] = None  # ISO 8601 date
    preferred_subjects: Optional[List[str]] = None  # ["Mathematics", "Physics"]
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    country: Optional[str] = None
    location: Optional[str] = None
    learning_style: Optional[LearningStyle] = None
    study_time_preference: Optional[StudyTimePreference] = None
    notification_settings: Optional[NotificationSettings] = None
    privacy_settings: Optional[PrivacySettings] = None


class AchievementBadge(BaseModel):
    """Achievement badge."""
    id: str
    name: str
    description: str
    icon: str
    earned_at: datetime


class ProfileResponse(BaseModel):
    """User profile response."""
    id: int
    phone_number: Optional[str]
    email: Optional[str]
    full_name: Optional[str]
    education_level: Optional[str]
    target_exam_date: Optional[datetime]
    preferred_subjects: Optional[List[str]]
    study_streak: int
    is_verified: bool
    created_at: datetime
    
    # Extended fields
    avatar_url: Optional[str]
    bio: Optional[str]
    country: Optional[str]
    location: Optional[str]
    learning_style: Optional[str]
    study_time_preference: Optional[str]
    notification_settings: Optional[NotificationSettings]
    privacy_settings: Optional[PrivacySettings]
    achievement_badges: Optional[List[AchievementBadge]]
    total_points: int
    level: int
    profile_completion_percentage: int
    
    class Config:
        from_attributes = True


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's profile.
    """
    # Parse JSON fields
    import json
    
    preferred_subjects = None
    if current_user.preferred_subjects:
        try:
            preferred_subjects = json.loads(current_user.preferred_subjects)
        except:
            preferred_subjects = []
    
    notification_settings = None
    if current_user.notification_settings:
        try:
            notification_settings = NotificationSettings(**json.loads(current_user.notification_settings))
        except:
            notification_settings = NotificationSettings()  # Default settings
    else:
        notification_settings = NotificationSettings()  # Default settings
    
    privacy_settings = None
    if current_user.privacy_settings:
        try:
            privacy_settings = PrivacySettings(**json.loads(current_user.privacy_settings))
        except:
            privacy_settings = PrivacySettings()  # Default settings
    else:
        privacy_settings = PrivacySettings()  # Default settings
    
    achievement_badges = []
    if current_user.achievement_badges:
        try:
            badges_data = json.loads(current_user.achievement_badges)
            achievement_badges = [AchievementBadge(**badge) for badge in badges_data]
        except:
            achievement_badges = []
    
    # Calculate profile completion percentage
    profile_completion = _calculate_profile_completion(current_user)
    
    return ProfileResponse(
        id=current_user.id,
        phone_number=current_user.phone_number,
        email=current_user.email,
        full_name=current_user.full_name,
        education_level=current_user.education_level,
        target_exam_date=current_user.target_exam_date,
        preferred_subjects=preferred_subjects,
        study_streak=current_user.study_streak,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        avatar_url=current_user.avatar_url,
        bio=current_user.bio,
        country=current_user.country,
        location=current_user.location,
        learning_style=current_user.learning_style,
        study_time_preference=current_user.study_time_preference,
        notification_settings=notification_settings,
        privacy_settings=privacy_settings,
        achievement_badges=achievement_badges,
        total_points=current_user.total_points or 0,
        level=current_user.level or 1,
        profile_completion_percentage=profile_completion
    )


@router.patch("/profile", response_model=ProfileResponse)
async def update_profile(
    updates: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile and preferences.
    
    Use cases:
    - Student progresses from JSS1 to JSS2 → update education_level
    - Student sets exam date → app can send reminders
    - Student chooses favorite subjects → filter sync to only those subjects
    """
    # Update fields if provided
    if updates.full_name is not None:
        current_user.full_name = updates.full_name
    
    if updates.education_level is not None:
        # Validate education level
        valid_levels = ["JSS1", "JSS2", "JSS3", "SSS1", "SSS2", "SSS3", "WASSCE", "GABECE", "NECO"]
        if updates.education_level not in valid_levels:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid education_level. Must be one of: {', '.join(valid_levels)}"
            )
        current_user.education_level = updates.education_level
    
    if updates.target_exam_date is not None:
        try:
            current_user.target_exam_date = datetime.fromisoformat(updates.target_exam_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use ISO 8601 (YYYY-MM-DD)"
            )
    
    if updates.preferred_subjects is not None:
        # Store as JSON string
        import json
        current_user.preferred_subjects = json.dumps(updates.preferred_subjects)
    
    if updates.avatar_url is not None:
        current_user.avatar_url = updates.avatar_url
    
    if updates.bio is not None:
        if len(updates.bio) > 500:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bio must be 500 characters or less"
            )
        current_user.bio = updates.bio
    
    if updates.country is not None:
        current_user.country = updates.country
    
    if updates.location is not None:
        current_user.location = updates.location
    
    if updates.learning_style is not None:
        current_user.learning_style = updates.learning_style.value
    
    if updates.study_time_preference is not None:
        current_user.study_time_preference = updates.study_time_preference.value
    
    if updates.notification_settings is not None:
        import json
        current_user.notification_settings = json.dumps(updates.notification_settings.dict())
    
    if updates.privacy_settings is not None:
        import json
        current_user.privacy_settings = json.dumps(updates.privacy_settings.dict())
    
    db.commit()
    db.refresh(current_user)
    
    # Parse JSON fields for response
    import json
    
    preferred_subjects = None
    if current_user.preferred_subjects:
        try:
            preferred_subjects = json.loads(current_user.preferred_subjects)
        except:
            preferred_subjects = []
    
    notification_settings = NotificationSettings()
    if current_user.notification_settings:
        try:
            notification_settings = NotificationSettings(**json.loads(current_user.notification_settings))
        except:
            pass
    
    privacy_settings = PrivacySettings()
    if current_user.privacy_settings:
        try:
            privacy_settings = PrivacySettings(**json.loads(current_user.privacy_settings))
        except:
            pass
    
    achievement_badges = []
    if current_user.achievement_badges:
        try:
            badges_data = json.loads(current_user.achievement_badges)
            achievement_badges = [AchievementBadge(**badge) for badge in badges_data]
        except:
            achievement_badges = []
    
    profile_completion = _calculate_profile_completion(current_user)
    
    return ProfileResponse(
        id=current_user.id,
        phone_number=current_user.phone_number,
        email=current_user.email,
        full_name=current_user.full_name,
        education_level=current_user.education_level,
        target_exam_date=current_user.target_exam_date,
        preferred_subjects=preferred_subjects,
        study_streak=current_user.study_streak,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        avatar_url=current_user.avatar_url,
        bio=current_user.bio,
        country=current_user.country,
        location=current_user.location,
        learning_style=current_user.learning_style,
        study_time_preference=current_user.study_time_preference,
        notification_settings=notification_settings,
        privacy_settings=privacy_settings,
        achievement_badges=achievement_badges,
        total_points=current_user.total_points or 0,
        level=current_user.level or 1,
        profile_completion_percentage=profile_completion
    )
