"""
AI Service for intelligent tutoring and explanations.
Uses Google Gemini for high-quality educational content.
"""
import google.generativeai as genai
from typing import List, Tuple, Optional
from app.core.config import settings
from app.models.question import Question
from app.api.v1.ai import ChatMessage


# Configure Gemini
try:
    genai.configure(api_key=getattr(settings, 'GEMINI_API_KEY', ''))
    model = genai.GenerativeModel('gemini-1.5-flash')
    GEMINI_AVAILABLE = True
except Exception as e:
    GEMINI_AVAILABLE = False
    model = None


async def generate_explanation(
    question: Question,
    student_answer: int,
    student_context: Optional[str] = None
) -> str:
    """
    Generate personalized explanation for why a student's answer was wrong.
    
    Args:
        question: The Question object
        student_answer: Index of option student selected (0-3)
        student_context: Optional context about student's confusion
    
    Returns:
        Detailed, pedagogical explanation
    """
    if not GEMINI_AVAILABLE or not model:
        # Fallback explanation
        return (
            f"The correct answer is option {chr(65 + question.correct_index)}. "
            f"{question.explanation or 'Review the key concepts for this topic.'}"
        )
    
    # Build prompt for Gemini
    import json
    options = json.loads(question.options_json)
    options_text = "\n".join([
        f"{chr(65 + i)}) {opt}"
        for i, opt in enumerate(options)
    ])
    
    prompt = f"""You are a patient West African exam tutor helping a student who got a question wrong.

Question: {question.content}

Options:
{options_text}

Correct Answer: {chr(65 + question.correct_index)}

Student's Answer: {chr(65 + student_answer)}

{f"Student's confusion: {student_context}" if student_context else ""}

Provide a clear, encouraging explanation that:
1. Acknowledges their answer
2. Explains why it's incorrect
3. Teaches the correct concept
4. Uses simple language appropriate for {question.difficulty.value} level
5. Relates to West African WAEC exam standards

Keep it under 150 words. Be encouraging!"""
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        # Fallback if Gemini fails
        return (
            f"You selected option {chr(65 + student_answer)}, but the correct answer is "
            f"option {chr(65 + question.correct_index)}. "
            f"{question.explanation or 'Please review this topic carefully.'}"
        )


async def chat_with_ai(
    message: str,
    history: List[ChatMessage],
    subject: Optional[str] = None,
    topic: Optional[str] = None,
    user_level: Optional[str] = None
) -> Tuple[str, List[str]]:
    """
    Have a conversational exchange with the AI tutor.
    
    Args:
        message: Student's current message
        history: Previous conversation messages
        subject: Subject context (MATHEMATICS, CHEMISTRY, etc.)
        topic: Specific topic context
        user_level: Student's education level
    
    Returns:
        Tuple of (response_text, suggested_follow_up_questions)
    """
    if not GEMINI_AVAILABLE or not model:
        raise Exception("AI service not available")
    
    # Build conversation context
    context_parts = [
        "You are a knowledgeable West African exam tutor specializing in WAEC preparation.",
        "You explain concepts clearly using examples relevant to West African students.",
        "You are patient, encouraging, and break down complex topics into simple parts."
    ]
    
    if subject:
        context_parts.append(f"Current subject: {subject}")
    if topic:
        context_parts.append(f"Current topic: {topic}")
    if user_level:
        context_parts.append(f"Student level: {user_level}")
    
    context = "\n".join(context_parts)
    
    # Build conversation history
    conversation = f"{context}\n\n"
    for msg in history[-5:]:  # Last 5 messages for context
        role = "Student" if msg.role == "user" else "Tutor"
        conversation += f"{role}: {msg.content}\n"
    
    conversation += f"Student: {message}\nTutor:"
    
    try:
        response = model.generate_content(conversation)
        response_text = response.text.strip()
        
        # Generate follow-up suggestions
        suggestions = _generate_suggestions(message, subject, topic)
        
        return response_text, suggestions
    
    except Exception as e:
        print(f"AI chat generation failed: {str(e)}")  # Debug logging
        raise Exception(f"AI generation failed: {str(e)}")


def _generate_suggestions(message: str, subject: Optional[str], topic: Optional[str]) -> List[str]:
    """Generate relevant follow-up question suggestions."""
    suggestions = []
    
    # Generic helpful suggestions
    if topic:
        suggestions.append(f"Can you explain {topic} with an example?")
        suggestions.append(f"What are common mistakes in {topic}?")
        suggestions.append(f"How is {topic} tested in WAEC?")
    
    if subject:
        suggestions.append(f"Show me practice questions on this")
        suggestions.append(f"What else should I know about {subject}?")
    
    return suggestions[:3]


def check_ai_quota(user_id: int) -> bool:
    """
    Check if user has remaining AI quota.
    
    Args:
        user_id: User ID to check
    
    Returns:
        True if user can make AI requests, False otherwise
    """
    # TODO: Implement quota tracking in database
    # For now, always return True
    return True


def increment_ai_usage(user_id: int, request_type: str = "explanation"):
    """
    Track AI usage for quota management.
    
    Args:
        user_id: User ID
        request_type: Type of request ("explanation" or "chat")
    """
    # TODO: Implement usage tracking in database
    pass
