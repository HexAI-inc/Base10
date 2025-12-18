"""Pydantic schemas for data validation and serialization."""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============= User Schemas =============

class UserRole(str, Enum):
    """Valid user roles."""
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


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


class UserLogin(BaseModel):
    """Schema for login (phone or email)."""
    identifier: str  # Can be phone or email
    password: str


class UserResponse(UserBase):
    """Schema for user data in responses."""
    id: int
    is_active: bool
    is_verified: bool
    role: str
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


# ============= Question Schemas =============

class DifficultyEnum(str, Enum):
    """Question difficulty."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class SubjectEnum(str, Enum):
    """WAEC subjects."""
    MATHEMATICS = "Mathematics"
    ENGLISH = "English Language"
    PHYSICS = "Physics"
    CHEMISTRY = "Chemistry"
    BIOLOGY = "Biology"


class QuestionBase(BaseModel):
    """Base question schema."""
    subject: SubjectEnum
    topic: str
    content: str
    options_json: str  # JSON string: '["A", "B", "C", "D"]'
    correct_index: int = Field(..., ge=0, le=3)
    explanation: Optional[str] = None
    exam_year: Optional[str] = None
    difficulty: DifficultyEnum = DifficultyEnum.MEDIUM


class QuestionCreate(QuestionBase):
    """Schema for creating questions."""
    pass


class QuestionResponse(QuestionBase):
    """Schema for question responses."""
    id: int
    
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
    subjects: Optional[List[SubjectEnum]] = None
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


# ============= Statistics Schemas =============

class SubjectStats(BaseModel):
    """Statistics for a specific subject."""
    subject: str
    total_attempts: int
    correct_attempts: int
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
