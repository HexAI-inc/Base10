"""System configuration endpoint for app versioning and maintenance."""
from fastapi import APIRouter
from pydantic import BaseModel
from app.models.enums import (
    Subject, DifficultyLevel, Topic, GradeLevel, 
    UserRole, AssignmentType, 
    AssignmentStatus, PostType, ReportReason, 
    ReportStatus, AssetType, OTPType
)
from app.schemas.schemas import NetworkTypeEnum

router = APIRouter()


class SystemConfig(BaseModel):
    """System configuration response."""
    min_app_version: str
    latest_app_version: str
    maintenance_mode: bool
    force_update: bool
    motd: str  # Message of the Day
    api_version: str
    features: dict


@router.get("/config", response_model=SystemConfig)
async def get_system_config():
    """
    Get system configuration for mobile app.
    
    Critical for production:
    - Force app updates if critical bugs found
    - Maintenance mode during database migrations
    - MOTD for important announcements
    
    Mobile app should check this on:
    1. App launch
    2. Before syncing
    3. After user login
    
    Example flow:
    ```
    if server.min_app_version > app.current_version:
        show_update_dialog(force=True)
        redirect_to_play_store()
    ```
    """
    return SystemConfig(
        min_app_version="1.0.0",  # Minimum required version
        latest_app_version="1.2.0",  # Latest available version
        maintenance_mode=False,  # Set to True during migrations
        force_update=False,  # Force users to update
        motd="Physics exams start next week! Good luck! 🎓",
        api_version="1.0.0",
        features={
            "flashcards_enabled": True,
            "voice_mode_enabled": True,
            "socratic_hints_enabled": True,
            "leaderboard_enabled": True,
            "offline_sync_enabled": True,
            "gemma_12b_enabled": True
        }
    )


@router.get("/health")
async def health_check():
    """
    Simple health check endpoint.
    
    Used by:
    - Load balancers
    - Monitoring systems
    - Deploy verification
    """
    return {
        "status": "healthy",
        "service": "Base10 API",
        "version": "1.0.0"
    }


@router.get("/")
async def root():
    """
    API root endpoint.
    """
    return {
        "app": "Base10 API",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
        "message": "Education for every student, everywhere 🌍"
    }


@router.get("/metadata/enums")
async def get_enums():
    """
    Get all enum values for frontend form validation and dropdowns.
    
    Returns all enum classes with their values for:
    - Form validation
    - Dropdown population
    - Type checking
    """
    return {
        "subjects": [{"value": s.value, "label": s.value.replace("_", " ").title()} for s in Subject],
        "difficulty_levels": [{"value": d.value, "label": d.value.replace("_", " ").title()} for d in DifficultyLevel],
        "topics": [{"value": t.value, "label": t.value.replace("_", " ").title()} for t in Topic],
        "grade_levels": [{"value": g.value, "label": g.value.replace("_", " ").title()} for g in GradeLevel],
        "user_roles": [{"value": r.value, "label": r.value.replace("_", " ").title()} for r in UserRole],
        "network_types": [{"value": n.value, "label": n.value.replace("_", " ").title()} for n in NetworkTypeEnum],
        "assignment_types": [{"value": a.value, "label": a.value.replace("_", " ").title()} for a in AssignmentType],
        "assignment_statuses": [{"value": a.value, "label": a.value.replace("_", " ").title()} for a in AssignmentStatus],
        "post_types": [{"value": p.value, "label": p.value.replace("_", " ").title()} for p in PostType],
        "report_reasons": [{"value": r.value, "label": r.value.replace("_", " ").title()} for r in ReportReason],
        "report_statuses": [{"value": r.value, "label": r.value.replace("_", " ").title()} for r in ReportStatus],
        "asset_types": [{"value": a.value, "label": a.value.replace("_", " ").title()} for a in AssetType],
        "otp_types": [{"value": o.value, "label": o.value.replace("_", " ").title()} for o in OTPType]
    }
