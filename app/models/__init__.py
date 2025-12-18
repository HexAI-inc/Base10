"""Initialize models module."""
from app.db.base import Base
from app.models.user import User
from app.models.question import Question
from app.models.enums import Subject, DifficultyLevel, Topic, ReportReason, ReportStatus
from app.models.progress import Attempt
from app.models.otp import OTP
from app.models.report import QuestionReport
from app.models.flashcard import FlashcardDeck, Flashcard, FlashcardReview
from app.models.classroom import Classroom, Assignment, ClassroomMaterial
from app.models.asset import Asset
from app.models.student_profile import StudentProfile, TeacherMessage
from app.models.marketing import WaitlistLead

# Export all models for alembic autogenerate
__all__ = [
    "Base", 
    "User", 
    "Question", 
    "Attempt", 
    "DifficultyLevel", 
    "Subject",
    "Topic",
    "ReportReason",
    "ReportStatus",
    "OTP",
    "QuestionReport",
    "ReportReason",
    "FlashcardDeck",
    "Flashcard",
    "FlashcardReview",
    "Classroom",
    "Assignment",
    "ClassroomMaterial",
    "Asset",
    "StudentProfile",
    "TeacherMessage",
    "WaitlistLead",
]
