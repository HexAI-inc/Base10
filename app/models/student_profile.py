"""Student profile for teacher notes, comments, and personalized tracking."""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class StudentProfile(Base):
    """
    Teacher's personalized notes and observations about a student in their classroom.
    
    Use Case:
    - Teacher tracks individual student progress per classroom
    - Stores notes, strengths, weaknesses, learning style
    - Enables personalized communication and AI context
    """
    __tablename__ = "student_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Links
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Teacher's observations
    notes = Column(Text, nullable=True)  # General notes about the student
    strengths = Column(Text, nullable=True)  # What they're good at
    weaknesses = Column(Text, nullable=True)  # Areas needing improvement
    learning_style = Column(String(100), nullable=True)  # "visual", "auditory", "kinesthetic"
    
    # Performance tracking (teacher's assessment)
    participation_level = Column(String(20), nullable=True)  # "high", "medium", "low"
    homework_completion_rate = Column(Float, nullable=True)  # 0.0 - 1.0
    
    # Communication
    last_contacted = Column(DateTime(timezone=True), nullable=True)
    contact_frequency = Column(String(20), nullable=True)  # "weekly", "monthly", "as_needed"
    
    # AI Context (for personalized AI responses)
    ai_context = Column(Text, nullable=True)  # Additional context for AI teacher
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    classroom = relationship("Classroom")
    student = relationship("User", foreign_keys=[student_id])
    teacher = relationship("User", foreign_keys=[teacher_id])
    
    def __repr__(self):
        return f"<StudentProfile classroom={self.classroom_id} student={self.student_id}>"


class TeacherMessage(Base):
    """
    Direct messages from teacher to student within classroom context.
    """
    __tablename__ = "teacher_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Links
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Message content
    subject = Column(String(200), nullable=True)
    message = Column(Text, nullable=False)
    message_type = Column(String(50), default="general")  # "encouragement", "concern", "reminder", "general"
    
    # Status
    is_read = Column(Integer, default=0)  # 0=unread, 1=read
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Tracking
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    classroom = relationship("Classroom")
    teacher = relationship("User", foreign_keys=[teacher_id])
    student = relationship("User", foreign_keys=[student_id])
    
    def __repr__(self):
        return f"<TeacherMessage from={self.teacher_id} to={self.student_id}>"
