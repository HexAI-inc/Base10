"""Question model for WAEC practice questions."""
from sqlalchemy import Column, Integer, String, Text, Enum as SQLEnum, DateTime, func, Index
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class DifficultyLevel(str, enum.Enum):
    """Question difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Subject(str, enum.Enum):
    """WAEC subjects."""
    MATHEMATICS = "Mathematics"
    ENGLISH = "English Language"
    PHYSICS = "Physics"
    CHEMISTRY = "Chemistry"
    BIOLOGY = "Biology"
    ECONOMICS = "Economics"
    GEOGRAPHY = "Geography"


class Question(Base):
    """
    Question bank for offline-first learning.
    
    Design notes:
    - Optimized for bulk sync (students download 100+ questions at once)
    - LaTeX support in 'content' field for math
    - options_json stores ["Option A", "Option B", "Option C", "Option D"]
    - correct_index is 0-3 (matches array index)
    """
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Categorization (indexed for fast filtering)
    subject = Column(SQLEnum(Subject), index=True, nullable=False)
    topic = Column(String, index=True, nullable=False)  # "Algebra", "Grammar", etc.
    
    # Question content
    content = Column(Text, nullable=False)  # Supports LaTeX: $x^2 + 3x - 4 = 0$
    options_json = Column(Text, nullable=False)  # JSON array as string
    correct_index = Column(Integer, nullable=False)  # 0, 1, 2, or 3
    explanation = Column(Text, nullable=True)
    
    # Metadata
    exam_year = Column(String, nullable=True)  # "WASSCE 2023"
    difficulty = Column(SQLEnum(DifficultyLevel), default=DifficultyLevel.MEDIUM)
    
    # Delta Sync Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete
    
    # Relationships
    attempts = relationship("Attempt", back_populates="question")
    
    # Index for delta sync queries
    __table_args__ = (
        Index('idx_updated_at', 'updated_at'),
    )
    
    def __repr__(self):
        return f"<Question {self.id}: {self.subject.value} - {self.topic}>"
