"""FastAPI main application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.session import engine
from app.db.base import Base
from app.api.v1 import (
    auth, 
    questions, 
    sync, 
    profile, 
    leaderboard, 
    flashcards, 
    reports, 
    ai, 
    student, 
    admin,
    marketing,
    voice,
    recovery,
    system,
    teacher,
    assets,
    billing,
    classrooms,
    ai_teacher,
    onboarding,
    moderation
)



@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup/shutdown events for the application.
    Creates database tables on startup.
    Starts scheduler for automated engagement (streaks, reminders, leaderboards).
    """
    # Startup
    print("🚀 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database ready!")
    
    # Start scheduler for automated engagement
    try:
        from app.services.scheduler import start_scheduler
        start_scheduler()
        print("⏰ Scheduler started - automated engagement active!")
    except Exception as e:
        print(f"⚠️  Failed to start scheduler: {e}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Base10 backend...")
    
    # Stop scheduler gracefully
    try:
        from app.services.scheduler import stop_scheduler
        stop_scheduler()
        print("⏰ Scheduler stopped")
    except Exception as e:
        print(f"⚠️  Failed to stop scheduler: {e}")


# Initialize FastAPI app
app = FastAPI(
    title="Base10 API",
    description="Offline-first education platform for rural African students",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc"  # ReDoc at /redoc
)

# CORS configuration for web app
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
# Authentication & Account Management
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(recovery.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(profile.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(onboarding.router, prefix="/api/v1/onboarding", tags=["Onboarding"])
app.include_router(moderation.router, prefix="/api/v1/moderation", tags=["Content Moderation"])

# Content & Learning
app.include_router(questions.router, prefix="/api/v1/questions", tags=["Questions"])
app.include_router(reports.router, prefix="/api/v1/questions", tags=["Questions"])
app.include_router(flashcards.router, prefix="/api/v1/flashcards", tags=["Flashcards"])

# AI & Intelligence (NEW - Strategic Addition #1)
# AI & Tutoring
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI Tutor"])
app.include_router(voice.router, prefix="/api/v1/voice", tags=["Voice AI"])
app.include_router(ai_teacher.router, prefix="/api/v1/ai-teacher", tags=["AI Teacher"])


# Assets & Optimization (NEW - Strategic Addition #2)
app.include_router(assets.router, prefix="/api/v1/assets", tags=["Assets"])

# Billing & Monetization (NEW - Strategic Addition #3)
app.include_router(billing.router, prefix="/api/v1/billing", tags=["Billing"])

# Sync & Leaderboard
app.include_router(sync.router, prefix="/api/v1/sync", tags=["Offline Sync"])
app.include_router(leaderboard.router, prefix="/api/v1/leaderboard", tags=["Leaderboard"])
app.include_router(teacher.router, prefix="/api/v1/teacher", tags=["Teacher"])
app.include_router(classrooms.router, prefix="/api/v1", tags=["Classrooms"])

# Student Dashboard & Analytics
app.include_router(student.router, prefix="/api/v1/student", tags=["Student Dashboard"])

# Marketing & Waitlist
app.include_router(marketing.router, prefix="/api/v1/marketing", tags=["Marketing"])

# Admin Dashboard & Monitoring
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])

# System & Config
app.include_router(system.router, prefix="/api/v1/system", tags=["System"])


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "app": "Base10 API",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
        "message": "Education for every student, everywhere 🌍"
    }


@app.get("/health")
def health_check():
    """Kubernetes/Docker health check."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Hot reload in development
    )
