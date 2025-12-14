"""Database session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# Engine configuration based on database type
engine_args = {
    "pool_pre_ping": True,  # Verify connections before using
}

# PostgreSQL-specific settings (not supported by SQLite)
if not settings.DATABASE_URL.startswith("sqlite"):
    engine_args.update({
        "pool_size": 10,        # Connection pool for scalability
        "max_overflow": 20
    })

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    **engine_args
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Dependency for getting database sessions.
    Use in FastAPI routes with Depends(get_db).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
