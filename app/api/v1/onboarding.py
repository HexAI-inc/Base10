"""Onboarding API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.schemas import schemas
from app.services.onboarding_service import OnboardingService
from app.models.enums import UserRole

router = APIRouter()

@router.get("/status", response_model=schemas.OnboardingStatusResponse)
async def get_onboarding_status(
    current_user: User = Depends(get_current_user)
):
    """Get current user's onboarding status."""
    return {
        "is_onboarded": current_user.is_onboarded,
        "onboarding_step": current_user.onboarding_step,
        "role": current_user.role
    }

@router.post("/student", response_model=schemas.UserResponse)
async def complete_student_onboarding(
    data: schemas.StudentOnboardingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete student onboarding."""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only students can use this endpoint"
        )
    
    onboarding_service = OnboardingService(db)
    updated_user = await onboarding_service.complete_student_onboarding(
        current_user, data.dict()
    )
    return updated_user

@router.post("/teacher", response_model=schemas.UserResponse)
async def complete_teacher_onboarding(
    data: schemas.TeacherOnboardingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete teacher onboarding."""
    if current_user.role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only teachers can use this endpoint"
        )
    
    onboarding_service = OnboardingService(db)
    updated_user = await onboarding_service.complete_teacher_onboarding(
        current_user, data.dict()
    )
    return updated_user
