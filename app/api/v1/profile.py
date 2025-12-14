"""User profile and preferences management."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.db.session import get_db
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter()


class ProfileUpdateRequest(BaseModel):
    """User profile update schema."""
    full_name: Optional[str] = None
    education_level: Optional[str] = None  # "JSS1", "JSS2", "JSS3", "WASSCE", "GABECE"
    target_exam_date: Optional[str] = None  # ISO 8601 date
    preferred_subjects: Optional[List[str]] = None  # ["Mathematics", "Physics"]


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
    
    class Config:
        from_attributes = True


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's profile.
    """
    # Parse preferred_subjects from JSON string if exists
    preferred_subjects = None
    if current_user.preferred_subjects:
        import json
        try:
            preferred_subjects = json.loads(current_user.preferred_subjects)
        except:
            preferred_subjects = []
    
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
        created_at=current_user.created_at
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
    
    db.commit()
    db.refresh(current_user)
    
    # Parse preferred_subjects for response
    preferred_subjects = None
    if current_user.preferred_subjects:
        import json
        try:
            preferred_subjects = json.loads(current_user.preferred_subjects)
        except:
            preferred_subjects = []
    
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
        created_at=current_user.created_at
    )
