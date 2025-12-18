"""
AI endpoints for intelligent tutoring.
Provides server-side AI explanations and chat using Gemini when online.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.user import User
from app.models.question import Question
from app.models.progress import Attempt
from app.api.v1.auth import get_current_user
from app.services.ai_service import (
    generate_ai_recommendations,
    check_ai_quota,
    increment_ai_usage,
    get_ai_quota_status
)


router = APIRouter()


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


@router.post("/explain", response_model=ExplainResponse)
async def explain_answer(
    request: ExplainRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate intelligent explanation for why a student's answer was wrong.
    
    This is the "Big Brain" - uses server-side Gemini to provide high-quality,
    personalized explanations when the student has internet connectivity.
    
    **Use Case**: Student just failed a question and wants to understand why.
    
    **Example**:
    ```json
    {
        "question_id": 402,
        "student_answer": 2,
        "context": "I thought isotopes had different atomic numbers"
    }
    ```
    
    **Response**:
    ```json
    {
        "explanation": "You chose option C, which states isotopes have different atomic numbers. This is incorrect. Isotopes are atoms of the same element (same atomic number) but with different numbers of neutrons, giving them different mass numbers...",
        "correct_answer": 1,
        "key_concepts": ["Atomic Structure", "Isotopes", "Mass Number"],
        "difficulty": "MEDIUM"
    }
    ```
    """
    # Fetch the question
    question = db.query(Question).filter(Question.id == request.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check Quota
    if not check_ai_quota(db, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI quota exceeded. Please wait for reset or upgrade."
        )
    
    # Check if student's answer is correct (shouldn't request explanation for correct answers)
    if request.student_answer == question.correct_index:
        return ExplainResponse(
            explanation="Actually, your answer is correct! Great job understanding this concept.",
            correct_answer=question.correct_index,
            key_concepts=[question.topic],
            difficulty=question.difficulty.value
        )
    
    # Generate AI explanation using service
    try:
        from app.services.ai_service import generate_explanation
        explanation_text = await generate_explanation(
            question=question,
            student_answer=request.student_answer,
            student_context=request.context
        )
    except ImportError:
        # Fallback explanation if AI service not configured
        explanation_text = (
            f"You selected option {chr(65 + request.student_answer)}, but the correct answer is "
            f"option {chr(65 + question.correct_index)}. "
            f"{question.explanation or 'Please review the key concepts for this topic.'}"
        )
    except Exception as e:
        # Fallback on any error
        explanation_text = f"The correct answer is option {chr(65 + question.correct_index)}. {question.explanation or 'Review this topic for better understanding.'}"
    
    # Increment usage
    increment_ai_usage(db, current_user.id, "explanation")
    
    return ExplainResponse(
        explanation=explanation_text,
        correct_answer=question.correct_index,
        key_concepts=[question.topic, question.subject.value],
        difficulty=question.difficulty.value
    )


@router.post("/chat", response_model=ChatResponse)
async def chat_tutor(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Conversational AI tutor for deep-dive learning.
    
    This is the "Online Tutor" - when students have connectivity, they can have
    extended conversations about topics they don't understand.
    
    **Use Case**: Student says "I don't understand Isotopes" and gets a conversation.
    
    **Example**:
    ```json
    {
        "message": "I don't understand isotopes",
        "history": [],
        "subject": "CHEMISTRY",
        "topic": "Atomic Structure"
    }
    ```
    
    **Response**:
    ```json
    {
        "response": "Great question! Isotopes are atoms of the same element that have the same number of protons but different numbers of neutrons. Think of it like siblings - they're from the same family (element) but have different weights. For example, Carbon-12 and Carbon-14 are both Carbon atoms...",
        "suggestions": [
            "Can you give me more examples of isotopes?",
            "How do isotopes affect atomic mass?",
            "What are radioactive isotopes?"
        ],
        "related_topics": ["Atomic Mass", "Radioactivity", "Nuclear Chemistry"]
    }
    ```
    """
    # Check Quota
    if not check_ai_quota(db, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI quota exceeded. Please wait for reset or upgrade."
        )

    # Check if AI service is available
    try:
        from app.services.ai_service import chat_with_ai
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="AI chat service is currently unavailable. Please try the question-specific explanations instead."
        )
    
    try:
        # Generate AI response using conversation history
        response_text, suggestions = await chat_with_ai(
            message=request.message,
            history=request.history,
            subject=request.subject,
            topic=request.topic,
            user_level=current_user.education_level,
            socratic_mode=request.socratic_mode
        )
        
        # Generate related topics based on subject
        related_topics = []
        if request.subject:
            # Could query database for related topics in the same subject
            related_topics = _get_related_topics(db, request.subject, request.topic)
        
        # Increment usage
        increment_ai_usage(db, current_user.id, "chat")
        
        return ChatResponse(
            response=response_text,
            suggestions=suggestions,
            related_topics=related_topics
        )
    
    except Exception as e:
        # Provide helpful fallback
        return ChatResponse(
            response=(
                f"I understand you're asking about {request.topic or 'this topic'}. "
                "While I'm having trouble generating a detailed response right now, "
                "I recommend reviewing the questions in this topic and using the "
                "explanation feature for specific questions you find challenging."
            ),
            suggestions=[
                "Try practicing questions on this topic",
                "Review the explanation for specific questions",
                "Ask about a specific concept you're struggling with"
            ],
            related_topics=[]
        )


def _get_related_topics(db: Session, subject: str, current_topic: Optional[str]) -> List[str]:
    """Get related topics in the same subject."""
    try:
        # Query distinct topics in the same subject
        topics = db.query(Question.topic).filter(
            Question.subject == subject
        ).distinct().limit(5).all()
        
        related = [t[0] for t in topics if t[0] != current_topic]
        return related[:3]
    except:
        return []


@router.get("/status")
async def ai_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check AI service availability and user's remaining quota.
    """
    # Check if services are available
    try:
        from app.services.ai_service import GEMINI_AVAILABLE
        services_available = GEMINI_AVAILABLE
    except ImportError:
        services_available = False
    
    # Get real quota status
    quota = get_ai_quota_status(db, current_user.id)
    
    return {
        "available": services_available,
        "quota_remaining": quota["remaining"],
        "quota_used": quota["used"],
        "quota_limit": quota["limit"],
        "features": {
            "explain": True,
            "chat": services_available,
            "quiz_generation": services_available,
            "socratic_mode": services_available,
            "premium": False
        },
        "message": "AI services ready" if services_available else "AI services not configured"
    }


@router.post("/generate-quiz")
async def generate_ai_quiz(
    subject: str = Query(..., description="Subject area (MATHEMATICS, CHEMISTRY, etc.)"),
    topic: Optional[str] = Query(None, description="Specific topic (optional)"),
    difficulty: str = Query("medium", regex="^(easy|medium|hard)$"),
    num_questions: int = Query(5, ge=1, le=10, description="Number of questions (1-10)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a custom AI quiz based on subject and topic.
    
    **Use Case**: Student wants practice questions on a specific topic or difficulty level.
    
    **Parameters**:
    - `subject`: Subject area (MATHEMATICS, CHEMISTRY, PHYSICS, etc.)
    - `topic`: Specific topic (optional, e.g., "Quadratic Equations", "Atomic Structure")
    - `difficulty`: Difficulty level (easy, medium, hard)
    - `num_questions`: How many questions to generate (1-10)
    
    **Example Request**:
    ```
    POST /ai/generate-quiz?subject=MATHEMATICS&topic=Quadratic Equations&difficulty=medium&num_questions=5
    ```
    
    **Response**:
    ```json
    {
        "title": "Quadratic Equations Quiz",
        "subject": "MATHEMATICS",
        "topic": "Quadratic Equations",
        "difficulty": "medium",
        "num_questions": 5,
        "questions": [
            {
                "question": "Solve the quadratic equation $x^2 - 5x + 6 = 0$",
                "options": {
                    "A": "$x = 2, 3$",
                    "B": "$x = -2, -3$",
                    "C": "$x = 1, 6$",
                    "D": "$x = -1, -6$"
                },
                "correct_answer": "A",
                "explanation": "Using factoring: $(x-2)(x-3) = 0$, so $x = 2$ or $x = 3$"
            }
        ]
    }
    ```
    """
    # Check Quota
    if not check_ai_quota(db, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI quota exceeded. Please wait for reset or upgrade."
        )

    try:
        from app.services.ai_service import generate_quiz
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="AI quiz generation service is currently unavailable."
        )
    
    try:
        quiz_data = await generate_quiz(
            subject=subject,
            topic=topic,
            difficulty=difficulty,
            num_questions=num_questions
        )
        
        # Increment usage
        increment_ai_usage(db, current_user.id, "quiz")
        
        return quiz_data
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate quiz: {str(e)}"
        )


@router.get("/recommendations")
async def get_ai_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized AI-generated study recommendations.
    
    Analyzes student's recent performance, weak topics, and exam readiness
    to provide actionable advice.
    """
    # 1. Gather performance data
    # Weak topics (accuracy < 70%)
    topic_stats = db.query(
        Question.topic,
        func.count(Attempt.id).label('attempts'),
        func.sum(case((Attempt.is_correct == True, 1), else_=0)).label('correct')
    ).join(
        Attempt, Attempt.question_id == Question.id
    ).filter(
        Attempt.user_id == current_user.id
    ).group_by(
        Question.topic
    ).all()
    
    weak_topics = []
    strong_topics = []
    for topic, attempts, correct in topic_stats:
        accuracy = (correct / attempts * 100) if attempts > 0 else 0
        if accuracy < 70:
            weak_topics.append(topic)
        elif accuracy >= 85:
            strong_topics.append(topic)
            
    # Overall stats
    stats = db.query(
        func.count(Attempt.id).label('total'),
        func.sum(case((Attempt.is_correct == True, 1), else_=0)).label('correct')
    ).filter(
        Attempt.user_id == current_user.id
    ).first()
    
    total = stats.total or 0
    correct = stats.correct or 0
    accuracy = (correct / total * 100) if total > 0 else 0
    
    performance_summary = {
        "weak_topics": weak_topics[:5],
        "strong_topics": strong_topics[:5],
        "overall_accuracy": round(accuracy, 2),
        "total_attempts": total,
        "days_until_exam": (current_user.target_exam_date - datetime.utcnow()).days if current_user.target_exam_date else None
    }
    
    # 2. Generate AI recommendations
    recommendations = await generate_ai_recommendations(performance_summary)
    
    if not recommendations:
        # Fallback
        return [
            {
                "title": "Keep Practicing!",
                "message": "Continue answering questions to get personalized AI recommendations.",
                "priority": "medium",
                "type": "coverage",
                "action": "practice_topics",
                "data": {}
            }
        ]
        
    return recommendations
