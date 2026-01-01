"""Pydantic schemas for data validation and serialization."""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from app.models.enums import (
    Subject, DifficultyLevel, GradeLevel, AssignmentType, 
    AssignmentStatus, PostType, Topic, ReportStatus, UserRole,
    AssetType, OTPType, QuestionType, NotificationType
)


# ============= User Schemas =============

class UserBase(BaseModel):
    """Base user schema."""
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = UserRole.STUDENT
    
    @validator('phone_number')
    def validate_phone(cls, v):
        """Validate phone number format (basic)."""
        if v and not v.startswith('+'):
            raise ValueError('Phone number must start with country code (+)')
        return v


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.STUDENT  # Force default, no admin creation via API
    
    @validator('role')
    def validate_role_creation(cls, v):
        """Prevent admin role creation via registration."""
        if v == UserRole.ADMIN:
            raise ValueError('Admin accounts cannot be created via registration')
        return v
    
    @validator('email', 'phone_number')
    def at_least_one_identifier(cls, v, values):
        """Ensure either email or phone is provided."""
        if not v and not values.get('phone_number') and not values.get('email'):
            raise ValueError('Either email or phone_number must be provided')
        return v


class UserUpdateAdmin(BaseModel):
    """Schema for admin to update user details."""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    total_points: Optional[int] = None
    level: Optional[int] = None
    study_streak: Optional[int] = None


class UserLogin(BaseModel):
    """Schema for login (phone or email)."""
    identifier: str  # Can be phone or email
    password: str


class UserResponse(UserBase):
    """Schema for user data in responses."""
    id: int
    is_active: bool
    is_verified: bool
    is_onboarded: bool
    onboarding_step: int
    role: UserRole
    ai_quota_limit: int
    ai_quota_used: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class DashboardStats(BaseModel):
    """User dashboard statistics."""
    total_attempts: int
    overall_accuracy: float
    streak_days: int
    study_time_hours: float
    due_reviews: int
    today_attempts: int
    has_target_exam: bool
    overview: Dict[str, Any]
    performance_trends: Dict[str, Any]
    topic_mastery: List[Dict[str, Any]]
    exam_readiness: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    time_analytics: Dict[str, Any]
    classmate_comparison: Dict[str, Any]


# ============= Onboarding Schemas =============

class StudentOnboardingRequest(BaseModel):
    """Schema for student onboarding."""
    education_level: GradeLevel  # Strict Enum
    preferred_subjects: List[Subject]
    target_exam_date: Optional[datetime] = None
    learning_style: Optional[str] = None
    study_time_preference: Optional[str] = None


class TeacherOnboardingRequest(BaseModel):
    """Schema for teacher onboarding."""
    bio: Optional[str] = None
    subjects_taught: List[Subject]
    school_name: Optional[str] = None
    first_classroom_name: str
    first_classroom_subject: Subject
    first_classroom_grade: GradeLevel


class OnboardingStatusResponse(BaseModel):
    """Schema for onboarding status."""
    is_onboarded: bool
    onboarding_step: int
    role: str


# ============= Asset Schemas =============

class AssetBase(BaseModel):
    """Base asset schema."""
    filename: str
    url: str
    asset_type: str
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    ai_metadata: Optional[Dict[str, Any]] = None


class AssetCreate(AssetBase):
    """Schema for creating assets."""
    uploaded_by_id: Optional[int] = None


class AssetResponse(AssetBase):
    """Schema for asset responses."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Question Schemas =============

class QuestionBase(BaseModel):
    """Base question schema."""
    subject: Subject
    topic: Topic
    content: str
    options_json: str  # JSON string: '["A", "B", "C", "D"]'
    correct_index: int = Field(..., ge=0, le=3)
    explanation: Optional[str] = None
    exam_year: Optional[str] = None
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    asset_id: Optional[int] = None


class QuestionCreate(QuestionBase):
    """Schema for creating questions."""
    pass


class QuestionResponse(QuestionBase):
    """Schema for question responses."""
    id: int
    asset: Optional[AssetResponse] = None
    
    class Config:
        from_attributes = True


class QuestionBulkSync(BaseModel):
    """Schema for syncing multiple questions to mobile."""
    questions: List[QuestionResponse]
    total: int
    synced_at: datetime


# ============= Attempt/Progress Schemas =============

class NetworkTypeEnum(str, Enum):
    """Network type when attempt was made."""
    WIFI = "wifi"
    FOUR_G = "4g"
    THREE_G = "3g"
    TWO_G = "2g"
    OFFLINE = "offline"


class AttemptCreate(BaseModel):
    """Schema for creating an attempt (from mobile offline data)."""
    question_id: int
    selected_option: int = Field(..., ge=0, le=3)
    is_correct: bool
    attempted_at: datetime
    device_id: Optional[str] = None
    
    # Psychometric fields (optional for backward compatibility)
    time_taken_ms: Optional[int] = Field(None, ge=0, description="Time taken in milliseconds")
    confidence_level: Optional[int] = Field(None, ge=1, le=5, description="1=Guessing, 5=Certain")
    network_type: Optional[NetworkTypeEnum] = Field(None, description="Network type during attempt")
    app_version: Optional[str] = Field(None, max_length=20, description="App version, e.g., 1.2.3")


class AttemptResponse(BaseModel):
    """Schema for attempt responses."""
    id: int
    user_id: int
    question_id: int
    is_correct: bool
    selected_option: int
    attempted_at: datetime
    
    class Config:
        from_attributes = True


class SyncPushRequest(BaseModel):
    """Schema for pushing offline attempts to server."""
    attempts: List[AttemptCreate]
    device_id: str


class SyncPushResponse(BaseModel):
    """Response after syncing attempts."""
    status: str
    synced_count: int
    failed_count: int = 0
    message: str


class SyncPullRequest(BaseModel):
    """
    Request for pulling new questions with delta sync.
    
    Delta Sync Logic:
    - If last_sync_timestamp is None: Full sync (return all questions up to limit)
    - If last_sync_timestamp provided: Return only questions where updated_at > last_sync_timestamp
    """
    last_sync_timestamp: Optional[datetime] = None  # Delta sync: only get changes since this time
    subjects: Optional[List[str]] = None  # Filter by subjects
    limit: int = Field(default=200, le=500)  # Mobile storage constraint
    subjects: Optional[List[Subject]] = None
    limit: int = Field(default=50, le=200)  # Max 200 questions per sync


class SyncPullResponse(BaseModel):
    """Response with questions and user stats."""
    questions: List[QuestionResponse]
    weak_topics: List[str]  # Topics where user has <50% accuracy
    total_attempts: int
    accuracy: float
    synced_at: datetime
    # New grades that were published since last sync (student-facing notifications)
    new_grades: Optional[List[dict]] = None


# ============= Marketing Schemas =============

class WaitlistCreate(BaseModel):
    """Schema for joining the waitlist."""
    full_name: str = Field(..., min_length=2, max_length=100)
    phone_number: str = Field(..., description="Phone number with country code")
    email: Optional[EmailStr] = None
    school_name: Optional[str] = None
    education_level: Optional[str] = None
    location: Optional[str] = None
    device_type: Optional[str] = None
    referral_source: Optional[str] = None


class WaitlistLeadResponse(WaitlistCreate):
    """Schema for waitlist lead data in responses."""
    id: int
    is_converted: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MarketingStats(BaseModel):
    """Schema for marketing analytics."""
    total_leads: int
    device_breakdown: Dict[str, str]
    top_schools: List[Dict[str, Any]]
    conversion_rate: float


class BroadcastRequest(BaseModel):
    """Schema for sending broadcast SMS."""
    message: str = Field(..., min_length=10, max_length=160)
    filter_location: Optional[str] = None
    filter_device: Optional[str] = None


# ============= Admin Profile Schemas =============

class AdminNotificationSettings(BaseModel):
    """Admin notification preferences."""
    email_enabled: bool = True
    system_alerts: bool = True  # Critical system issues
    user_reports: bool = True  # Content moderation reports
    new_registrations: bool = False  # Daily digest of new users
    performance_alerts: bool = True  # Performance degradation
    security_alerts: bool = True  # Suspicious activity


class AdminPreferences(BaseModel):
    """Admin dashboard preferences."""
    theme: str = "light"  # "light" or "dark"
    default_view: str = "dashboard"  # Default page on login
    items_per_page: int = 25  # Pagination size
    auto_refresh_interval: int = 60  # Seconds, 0 = disabled
    show_advanced_metrics: bool = True
    timezone: str = "UTC"


class AdminProfileResponse(BaseModel):
    """Admin profile response with system-specific fields."""
    id: int
    email: Optional[str]
    phone_number: Optional[str]
    username: Optional[str]
    full_name: Optional[str]
    role: UserRole
    avatar_url: Optional[str]
    bio: Optional[str]
    
    # Admin-specific fields
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    # Settings
    notification_settings: Optional[AdminNotificationSettings]
    preferences: Optional[AdminPreferences]
    
    # Permissions & access
    total_actions_performed: int = 0  # Count of admin actions
    last_action_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AdminProfileUpdate(BaseModel):
    """Schema for updating admin profile."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)


class AdminSettingsUpdate(BaseModel):
    """Schema for updating admin settings."""
    notification_settings: Optional[AdminNotificationSettings] = None
    preferences: Optional[AdminPreferences] = None


class AdminActivityLog(BaseModel):
    """Admin activity log entry."""
    id: int
    admin_id: int
    admin_name: str
    action_type: str  # "user_update", "content_moderation", "system_config", etc.
    action_description: str
    target_type: Optional[str] = None  # "user", "question", "classroom", etc.
    target_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None  # Additional context
    ip_address: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True


class AdminActivityResponse(BaseModel):
    """Response for admin activity logs."""
    activities: List[AdminActivityLog]
    total: int
    page: int
    page_size: int


# ============= Statistics Schemas =============

class SubjectStats(BaseModel):
    """Statistics for a specific subject."""
    subject_name: str
    total_attempts: int
    accuracy: float
    mastery_level: str
    top_topics: List[str]


class UserStats(BaseModel):
    """User progress statistics."""
    total_attempts: int
    correct_attempts: int
    accuracy: float
    subjects_breakdown: List[SubjectStats]
    weak_topics: List[str]
    streak_days: int


# ============= AI Schemas =============

class ExplainRequest(BaseModel):
    """Request to explain why a student's answer was wrong."""
    question_id: int = Field(..., description="The question ID the student attempted")
    student_answer: int = Field(..., ge=0, le=3, description="The option index (0-3) the student selected")
    context: Optional[str] = Field(None, description="Additional context about student's confusion")


class ExplainResponse(BaseModel):
    """AI-generated explanation tailored to student's mistake."""
    explanation: str = Field(..., description="Detailed explanation of why the answer was wrong and how to approach it correctly")
    correct_answer: int = Field(..., description="The correct option index")
    key_concepts: List[str] = Field(default_factory=list, description="Key concepts the student should review")
    difficulty: str = Field(..., description="Question difficulty level")


class ChatMessage(BaseModel):
    """A single message in the conversation."""
    role: str = Field(..., description="Either 'user' or 'assistant'")
    content: str = Field(..., description="The message content")


class ChatRequest(BaseModel):
    """Request for conversational AI tutoring."""
    message: str = Field(..., min_length=1, max_length=1000, description="Student's question or message")
    history: List[ChatMessage] = Field(default_factory=list, description="Previous conversation history")
    subject: Optional[str] = Field(None, description="Subject context (MATHEMATICS, PHYSICS, etc.)")
    topic: Optional[str] = Field(None, description="Specific topic for context")
    socratic_mode: bool = Field(False, description="Use Socratic teaching method (guide student to discover answer)")


class ChatResponse(BaseModel):
    """AI tutor's response."""
    response: str = Field(..., description="AI tutor's helpful response")
    suggestions: List[str] = Field(default_factory=list, description="Follow-up question suggestions")
    related_topics: List[str] = Field(default_factory=list, description="Related topics to explore")


# ============= Flashcard Schemas =============

class FlashcardBase(BaseModel):
    """Base flashcard schema."""
    front: str
    back: str
    asset_id: Optional[int] = None


class FlashcardCreate(FlashcardBase):
    """Schema for creating flashcards."""
    deck_id: int


class FlashcardResponse(FlashcardBase):
    """Schema for flashcard responses."""
    id: int
    asset: Optional[AssetResponse] = None
    
    class Config:
        from_attributes = True


class FlashcardDeckBase(BaseModel):
    """Base flashcard deck schema."""
    name: str
    description: Optional[str] = None
    subject: Subject
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM


class FlashcardDeckCreate(FlashcardDeckBase):
    """Schema for creating flashcard decks."""
    pass


class FlashcardDeckResponse(FlashcardDeckBase):
    """Schema for flashcard deck responses."""
    id: int
    card_count: int
    cards: List[FlashcardResponse] = []
    
    class Config:
        from_attributes = True


# ============= Classroom & Assignment Schemas =============

class ClassroomCreate(BaseModel):
    """Schema for creating a classroom."""
    name: str = Field(..., min_length=3, max_length=100, description="Classroom name")
    description: Optional[str] = Field(None, max_length=500)
    subject: Optional[Subject] = None
    grade_level: Optional[GradeLevel] = None


class ClassroomResponse(BaseModel):
    """Schema for classroom responses."""
    id: int
    name: str
    description: Optional[str]
    join_code: str
    is_active: int
    student_count: int
    subject: Optional[Subject] = None
    grade_level: Optional[GradeLevel] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ClassroomJoin(BaseModel):
    """Schema for students joining a classroom."""
    join_code: str = Field(..., min_length=7, max_length=12)


class AssignmentCreate(BaseModel):
    """Schema for creating an assignment."""
    classroom_id: int
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    subject_filter: Optional[Subject] = None
    topic_filter: Optional[Topic] = None
    difficulty_filter: Optional[DifficultyLevel] = None
    question_count: int = Field(default=10, ge=1, le=50)
    due_date: Optional[datetime] = None


class AssignmentResponse(BaseModel):
    """Schema for assignment responses."""
    id: int
    classroom_id: int
    title: str
    description: Optional[str]
    subject_filter: Optional[Subject] = None
    topic_filter: Optional[Topic] = None
    question_count: int
    due_date: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class StudentPerformance(BaseModel):
    """Individual student performance in a classroom."""
    user_id: int
    full_name: str
    total_attempts: int
    correct_attempts: int
    accuracy: float
    avg_time_ms: Optional[float]
    guessing_rate: float  # % of attempts < 2 seconds
    struggle_rate: float  # % of attempts > 60 seconds
    misconception_count: int  # High confidence + wrong


class TopicPerformance(BaseModel):
    """Performance by topic."""
    topic: str
    total_attempts: int
    accuracy: float
    avg_confidence: Optional[float]
    struggling_students: int


class ClassroomAnalytics(BaseModel):
    """Comprehensive classroom analytics."""
    classroom_id: int
    classroom_name: str
    total_students: int
    active_students: int  # Students with attempts in last 7 days
    
    # Overall metrics
    total_attempts: int
    average_accuracy: float
    average_confidence: Optional[float] = None
    
    # Psychometric insights
    avg_time_per_question_ms: Optional[float]
    guessing_rate: float
    struggle_rate: float
    
    # Per-student breakdown
    students: List[StudentPerformance]
    
    # Per-topic breakdown
    topics: List[TopicPerformance]


class StreamPostCreate(BaseModel):
    """Schema for creating a stream post."""
    content: str = Field(..., min_length=1)
    attachment_url: Optional[str] = None


class StreamPostResponse(BaseModel):
    """Schema for stream post responses."""
    id: int
    classroom_id: int
    author_id: int
    content: str
    post_type: str
    attachment_url: Optional[str]
    parent_post_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class MaterialCreate(BaseModel):
    """Schema for creating classroom material."""
    title: str
    description: Optional[str] = None
    asset_id: Optional[int] = None


class ClassroomUpdate(BaseModel):
    """Schema for updating a classroom."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    subject: Optional[str] = Field(None, max_length=100)
    grade_level: Optional[str] = Field(None, max_length=50)


class AssignmentUpdate(BaseModel):
    """Schema for updating an assignment."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    subject_filter: Optional[str] = None
    topic_filter: Optional[str] = None
    difficulty_filter: Optional[str] = None
    question_count: Optional[int] = Field(None, gt=0)
    assignment_type: Optional[str] = None
    max_points: Optional[int] = Field(None, gt=0)
    status: Optional[str] = None
    due_date: Optional[datetime] = None


class MaterialUpdate(BaseModel):
    """Schema for updating classroom material."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    asset_id: Optional[int] = None
    url: Optional[str] = None


class MaterialResponse(BaseModel):
    """Schema for classroom material responses."""
    id: int
    classroom_id: int
    uploaded_by_id: int
    title: Optional[str]
    description: Optional[str]
    asset_id: Optional[int]
    url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ManualAssignmentCreate(BaseModel):
    """Schema for creating a manual assignment."""
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    points: Optional[int] = 100


class SubmissionCreate(BaseModel):
    """Schema for creating a submission."""
    content_text: Optional[str] = None
    attachment_url: Optional[str] = None


class GradeCreate(BaseModel):
    """Schema for grading a submission."""
    grade: int = Field(..., ge=0, le=100)
    feedback: Optional[str] = None


# ============= Teacher AI Assistant Schemas =============

class TeacherAIRequest(BaseModel):
    """Request for teacher AI assistant."""
    message: str = Field(..., min_length=3, max_length=2000, description="Teacher's natural language command")
    classroom_id: Optional[int] = Field(None, description="Optional classroom context")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class QuizQuestion(BaseModel):
    """Generated quiz question."""
    id: int
    content: str
    options: List[str]
    correct_index: int
    explanation: Optional[str]
    subject: Optional[str]
    topic: Optional[str]
    difficulty: Optional[str]


class QuizDraft(BaseModel):
    """Draft quiz for teacher review."""
    questions: List[QuizQuestion]
    total_found: int
    requested: int
    source: str = "database"
    parameters: Dict[str, Any]


class PerformanceAnalysis(BaseModel):
    """Classroom performance analysis."""
    classroom_name: str
    time_period: str
    total_students: int
    active_students: int
    total_attempts: int
    accuracy: float
    avg_time_seconds: Optional[float]
    guessing_rate: float
    struggle_rate: float
    insights: List[str]


class StrugglingStudent(BaseModel):
    """Student who needs help."""
    student_id: int
    student_name: str
    accuracy: float
    total_attempts: int
    misconception_rate: float
    needs_help_with: str


class StrugglingStudentsReport(BaseModel):
    """Report of struggling students."""
    classroom_name: str
    total_students: int
    struggling_count: int
    students: List[StrugglingStudent]
    recommendations: List[str]


class ClassroomReport(BaseModel):
    """Comprehensive classroom report."""
    summary: str
    performance_metrics: PerformanceAnalysis
    struggling_students: StrugglingStudentsReport
    generated_at: str


class TeacherAIResponse(BaseModel):
    """Response from teacher AI assistant."""
    intent: Optional[str] = None
    confidence: Optional[float] = None
    parameters: Optional[Dict[str, Any]] = None
    action_summary: Optional[str] = None
    requires_approval: bool = False
    questions_to_clarify: List[str] = []
    
    # Intent-specific data
    quiz_data: Optional[QuizDraft] = None
    analysis: Optional[PerformanceAnalysis] = None
    struggling_students: Optional[StrugglingStudentsReport] = None
    report: Optional[ClassroomReport] = None
    
    # Error handling
    error: Optional[str] = None
    message: Optional[str] = None
    raw_response: Optional[str] = None


class ApproveQuizRequest(BaseModel):
    """Request to approve and send quiz to students."""
    question_ids: List[int] = Field(..., min_items=1, description="Selected question IDs")
    classroom_id: int = Field(..., description="Classroom to send quiz to")
    title: str = Field(..., min_length=3, max_length=200, description="Quiz title")
    description: Optional[str] = Field(None, description="Quiz description")
    due_date: Optional[datetime] = Field(None, description="Due date")
    points_per_question: int = Field(default=10, ge=1, le=100, description="Points for each correct answer")
