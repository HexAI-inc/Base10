"""Database session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,        # Connection pool for scalability
    max_overflow=20
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
