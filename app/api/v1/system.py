"""System configuration endpoint for app versioning and maintenance."""
from fastapi import APIRouter
from pydantic import BaseModel

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
            "gpt_5_1_codex_max_enabled": True
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
