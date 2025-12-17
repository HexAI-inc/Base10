"""Initialize models module."""
from app.db.base import Base
from app.models.user import User
from app.models.question import Question, DifficultyLevel, Subject
from app.models.progress import Attempt
from app.models.otp import OTP
from app.models.report import QuestionReport, ReportReason
from app.models.flashcard import FlashcardDeck, Flashcard, FlashcardReview
from app.models.classroom import Classroom, Assignment
from app.models.student_profile import StudentProfile, TeacherMessage

# Export all models for alembic autogenerate
__all__ = [
    "Base", 
    "User", 
    "Question", 
    "Attempt", 
    "DifficultyLevel", 
    "Subject",
    "OTP",
    "QuestionReport",
    "ReportReason",
    "FlashcardDeck",
    "Flashcard",
    "FlashcardReview",
    "Classroom",
    "Assignment",
    "StudentProfile",
    "TeacherMessage",
]
