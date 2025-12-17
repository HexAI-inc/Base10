"""Classroom and Assignment models for teacher features."""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Table, Boolean
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
    subject = Column(String(50), nullable=True)  # "Mathematics", "Physics", etc.
    grade_level = Column(String(20), nullable=True)  # "JSS1", "JSS2", "JSS3", "SS1", etc.
    join_code = Column(String(12), unique=True, index=True, nullable=False)  # e.g., "MATH-778"
    
    # Status
    is_active = Column(Boolean, default=True)  # True=active, False=archived
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    teacher = relationship("User", foreign_keys=[teacher_id])
    students = relationship("User", secondary=classroom_students, backref="enrolled_classes")
    assignments = relationship("Assignment", back_populates="classroom", cascade="all, delete-orphan")
    posts = relationship("ClassroomPost", back_populates="classroom", cascade="all, delete-orphan")
    materials = relationship("ClassroomMaterial", back_populates="classroom", cascade="all, delete-orphan")
    
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
    
    # Assignment type and AI support
    assignment_type = Column(String(20), default="quiz")  # "quiz", "manual", "essay"
    max_points = Column(Integer, default=100)
    is_ai_generated = Column(Integer, default=0)  # 0=manual, 1=AI generated
    status = Column(String(20), default="draft")  # "draft", "published", "archived"
    
    # Timing
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    classroom = relationship("Classroom", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Assignment {self.title} for classroom {self.classroom_id}>"


# Classroom stream posts (announcements, discussion posts, assignment alerts)
class ClassroomPost(Base):
    __tablename__ = "classroom_posts"

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    post_type = Column(String(30), default="announcement")  # announcement, discussion, assignment_alert, comment
    parent_post_id = Column(Integer, ForeignKey("classroom_posts.id"), nullable=True)
    attachment_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    classroom = relationship("Classroom", back_populates="posts")
    author = relationship("User")
    # Hierarchical comments
    parent = relationship("ClassroomPost", remote_side=[id], backref="comments")


# Classroom materials (files, PDFs, images)
class ClassroomMaterial(Base):
    __tablename__ = "classroom_materials"

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False, index=True)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    asset_id = Column(String, nullable=True)  # Link to asset record or filename
    title = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    classroom = relationship("Classroom", back_populates="materials")
    uploader = relationship("User")


# Student submissions for manual/essay assignments
class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    content_text = Column(Text, nullable=True)
    attachment_url = Column(String, nullable=True)

    # AI draft suggestions
    ai_suggested_score = Column(Integer, nullable=True)
    ai_feedback_draft = Column(Text, nullable=True)

    # Final grade and feedback
    grade = Column(Integer, nullable=True)
    feedback = Column(Text, nullable=True)
    status = Column(String(20), default="submitted")  # submitted, graded, late
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    graded_at = Column(DateTime(timezone=True), nullable=True)
    is_graded = Column(Integer, default=0)

    # Relationships
    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User")
