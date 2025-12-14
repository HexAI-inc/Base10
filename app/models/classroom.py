"""Classroom and Assignment models for teacher features."""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import secrets


# Association table for many-to-many relationship between classrooms and students
classroom_students = Table(
    'classroom_students',
    Base.metadata,
    Column('classroom_id', Integer, ForeignKey('classrooms.id'), primary_key=True),
    Column('student_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('joined_at', DateTime(timezone=True), server_default=func.now())
)


class Classroom(Base):
    """
    Virtual classroom for teachers to manage students.
    
    Use Case:
    - Teacher creates classroom: "JSS3 Mathematics A"
    - Gets join code: "MATH-778"
    - Students enter code in app → auto-join classroom
    - Teacher assigns homework → appears in student's app
    - Teacher views aggregate analytics per class
    """
    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)
    
    # Teacher who owns this classroom
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Classroom details
    name = Column(String(100), nullable=False)  # e.g., "JSS3 Mathematics A"
    description = Column(Text, nullable=True)
    join_code = Column(String(12), unique=True, index=True, nullable=False)  # e.g., "MATH-778"
    
    # Status
    is_active = Column(Integer, default=1)  # 1=active, 0=archived
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    teacher = relationship("User", foreign_keys=[teacher_id])
    students = relationship("User", secondary=classroom_students, backref="enrolled_classes")
    assignments = relationship("Assignment", back_populates="classroom", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Classroom {self.name} ({self.join_code})>"
    
    @staticmethod
    def generate_join_code():
        """Generate a unique 6-character join code like MATH-778."""
        # Simple implementation - can be improved with collision checking
        prefix = "".join(secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ") for _ in range(4))
        suffix = "".join(secrets.choice("23456789") for _ in range(3))
        return f"{prefix}-{suffix}"


class Assignment(Base):
    """
    Homework/practice assignments for a classroom.
    
    Flow:
    1. Teacher creates assignment for specific topic/subject
    2. Assignment pushed to all students in classroom
    3. Students complete questions offline
    4. Sync brings results back → teacher sees aggregate performance
    """
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    
    # Which classroom is this for
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False, index=True)
    
    # Assignment details
    title = Column(String(200), nullable=False)  # e.g., "Week 5 Algebra Practice"
    description = Column(Text, nullable=True)
    
    # Question filters (used to select which questions to assign)
    subject_filter = Column(String(50), nullable=True)  # "Mathematics", "Physics", etc.
    topic_filter = Column(String(100), nullable=True)  # "Quadratic Equations", "Mechanics"
    difficulty_filter = Column(String(20), nullable=True)  # "easy", "medium", "hard"
    
    # Number of questions to assign (random selection from filters)
    question_count = Column(Integer, default=10)
    
    # Timing
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    classroom = relationship("Classroom", back_populates="assignments")
    
    def __repr__(self):
        return f"<Assignment {self.title} for classroom {self.classroom_id}>"
