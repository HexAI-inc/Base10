"""
AI Service for intelligent tutoring and explanations.
Uses Google Gemini for high-quality educational content with Socratic teaching.
"""
import google.generativeai as genai
import re
import json
import logging
from typing import List, Tuple, Optional, Dict, Any
from app.core.config import settings
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.question import Question
from app.schemas.schemas import ChatMessage

logger = logging.getLogger(__name__)

# Configure Gemini
try:
    GOOGLE_API_KEY = getattr(settings, 'GOOGLE_API_KEY', '') or getattr(settings, 'GEMINI_API_KEY', '')
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    GEMINI_AVAILABLE = bool(GOOGLE_API_KEY)
except Exception as e:
    logger.error(f"Failed to configure Gemini: {e}")
    GEMINI_AVAILABLE = False
    model = None


# System Prompts
SYSTEM_PROMPT = """
You are "Base10", an advanced WAEC Tutor AI.

CRITICAL RULES:
1. BE ACCURATE: Only provide information you are certain about. If unsure, say "I'm not completely certain, but..."
2. NO FABRICATION: Do not make up facts, formulas, or information. Stick to established WAEC curriculum content.
3. ADMIT LIMITATIONS: If asked about something outside your knowledge, say so clearly.

TEACHING GUIDELINES:
1. PERSONA: Patient, encouraging, and clear.
2. MATH/SCIENCE NOTATION: 
   - Wrap formulas/equations in $ signs for LaTeX: $E = mc^2$
   - Use plain text for units: kg, K, J, m/s (NOT $\\text{kg}$)
   - Variables in LaTeX: $Q = mc\\Delta T$
   - Fractions: $\\frac{a}{b}$
   - Powers: $x^2$ or $x^{10}$
   - Square roots: $\\sqrt{x}$
   - Greek letters: $\\theta$, $\\Delta$, $\\pi$
   - Chemical formulas: $H^+$, $H_2O$, $Ca^{2+}$, $SO_4^{2-}$
   - NEVER use \\text{} or \\mathrm{} - they break rendering
   - Example: "The mass is 5 kg and energy is $E = \\frac{1}{2}mv^2$"
3. CONTEXT AWARENESS: Pay attention to the subject and topic being discussed.
4. MODES:
   - CHAT MODE (default): When user asks for help, explanation, "how to", "solve this", or "explain" - EXPLAIN thoroughly and accurately.
   - QUIZ MODE: ONLY when user explicitly asks for "quiz", "test", "practice questions", or "exercises".
   - TRIGGER: If Quiz Mode is active, output: [QUIZ_MODE: Subject | Topic]
5. STAY ON TOPIC: Focus on the current subject. Don't randomly switch topics or add unrelated information.
"""

SOCRATIC_PROMPT = """
You are "Base10", a Socratic WAEC Tutor AI designed to help students THINK, not just get answers.

CRITICAL RULES:
1. BE ACCURATE: Only provide information you are certain about. If unsure, say "I'm not completely certain, but..."
2. NO FABRICATION: Do not make up facts, formulas, or information. Stick to established WAEC curriculum content.
3. ADMIT LIMITATIONS: If asked about something outside your knowledge, say so clearly.

SOCRATIC TEACHING METHOD:
1. NEVER GIVE THE FINAL ANSWER DIRECTLY: Instead, guide the student with leading questions.
2. ASK GUIDING QUESTIONS: Help the student discover the solution themselves.
3. BREAK DOWN PROBLEMS: Split complex problems into smaller, manageable steps.
4. VALIDATE REASONING: When student answers a guiding question, confirm if correct and ask the next step.
5. ENCOURAGE THINKING: Use phrases like:
   - "What do you think happens if...?"
   - "Can you identify the first step?"
   - "What formula might help here?"
   - "How would you approach this?"

EXAMPLES OF SOCRATIC RESPONSES:

Bad (Direct Answer):
User: "What is 2x + 4 = 10?"
AI: "x = 3"

Good (Socratic):
User: "What is 2x + 4 = 10?"
AI: "Great question! To solve for x, we first need to isolate the term with x. What happens if we subtract 4 from both sides?"

MATH/SCIENCE NOTATION (same as default):
   - Use LaTeX for formulas: $E = mc^2$
   - Plain text for units: kg, K, J
   - NEVER use \\text{} or \\rightarrow

6. STAY ON TOPIC: Focus on the current subject.
"""


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
    user_level: Optional[str] = None,
    socratic_mode: bool = False
) -> Tuple[str, List[str]]:
    """
    Have a conversational exchange with the AI tutor.
    
    Args:
        message: Student's current message
        history: Previous conversation messages
        subject: Subject context (MATHEMATICS, CHEMISTRY, etc.)
        topic: Specific topic context
        user_level: Student's education level
        socratic_mode: If True, use Socratic teaching method
    
    Returns:
        Tuple of (response_text, suggested_follow_up_questions)
    """
    if not GEMINI_AVAILABLE or not model:
        raise Exception("AI service not available")
    
    # Choose prompt based on mode
    system_prompt = SOCRATIC_PROMPT if socratic_mode else SYSTEM_PROMPT
    
    # Build conversation history for Gemini
    gemini_history = []
    for msg in history[-10:]:  # Last 10 messages for context
        role = "user" if msg.role == "user" else "model"
        gemini_history.append({"role": role, "parts": [msg.content]})
    
    # Add subject context to current message
    if subject:
        message = f"(Current Subject: {subject}) {message}"
    
    try:
        # Create chat with system instruction
        chat_model = genai.GenerativeModel(
            'gemini-1.5-flash',
            system_instruction=system_prompt
        )
        
        chat = chat_model.start_chat(history=gemini_history)
        response = chat.send_message(message)
        response_text = response.text.strip()
        
        # Check for quiz mode trigger
        quiz_match = re.search(r'\[QUIZ_MODE:\s*(.*?)\s*\|\s*(.*?)\]', response_text)
        if quiz_match:
            quiz_subject = quiz_match.group(1).strip()
            quiz_topic = quiz_match.group(2).strip()
            # Remove the trigger from response
            response_text = re.sub(r'\[QUIZ_MODE:.*?\]', '', response_text).strip()
            if not response_text:
                response_text = f"Starting {quiz_subject} Quiz on {quiz_topic}..."
        
        # Generate follow-up suggestions
        suggestions = _generate_suggestions(message, subject, topic, socratic_mode)
        
        return response_text, suggestions
    
    except Exception as e:
        logger.error(f"AI chat generation failed: {str(e)}")
        raise Exception(f"AI generation failed: {str(e)}")


def _generate_suggestions(message: str, subject: Optional[str], topic: Optional[str], socratic: bool = False) -> List[str]:
    """Generate contextual follow-up suggestions."""
    suggestions = []
    
    message_lower = message.lower()
    
    if socratic:
        # Socratic mode suggestions - guide deeper thinking
        if any(word in message_lower for word in ['why', 'how', 'what if']):
            suggestions.append("Can you explain that in your own words?")
            suggestions.append("What makes you think that?")
        else:
            suggestions.append("What do you think would happen if...?")
            suggestions.append("How does this connect to what you learned before?")
    else:
        # Direct help mode suggestions
        if 'example' in message_lower:
            suggestions.append("Can you show another example?")
            suggestions.append("How would this work in a different scenario?")
        elif any(word in message_lower for word in ['explain', 'understand', 'confused']):
            suggestions.append("Can you break this down further?")
            suggestions.append("Show me a worked example")
        else:
            suggestions.append("Tell me more about this")
            suggestions.append("Why is this important?")
    
    if subject and topic:
        suggestions.append(f"Give me a practice question on {topic}")
    
    return suggestions[:3]  # Return top 3


def clean_for_speech(text: str) -> str:
    """
    Convert LaTeX and mathematical notation to speech-friendly text.
    Useful for audio output or accessibility.
    """
    # Remove LaTeX delimiters
    text = re.sub(r'\$\$(.*?)\$\$', r'\1', text)
    text = re.sub(r'\$(.*?)\$', r'\1', text)
    
    # Replace common LaTeX commands
    replacements = {
        r'\\frac\{(.*?)\}\{(.*?)\}': r'\1 over \2',
        r'\\sqrt\{(.*?)\}': r'square root of \1',
        r'\\text\{(.*?)\}': r'\1',
        r'\^': ' to the power of ',
        r'_': ' subscript ',
        r'\\times': ' times ',
        r'\\div': ' divided by ',
        r'\\pm': ' plus or minus ',
        r'\\leq': ' less than or equal to ',
        r'\\geq': ' greater than or equal to ',
        r'\\neq': ' not equal to ',
        r'\\approx': ' approximately equal to ',
    }
    
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)
    
    # Clean up extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def sanitize_json_output(text: str) -> str:
    """
    Properly escape LaTeX in JSON output to prevent rendering issues.
    Ensures \\text{} and other LaTeX commands work correctly.
    """
    # Don't double-escape already escaped backslashes
    if '\\\\' not in text:
        # Escape single backslashes for JSON
        text = text.replace('\\', '\\\\')
    
    return text


async def generate_quiz(
    subject: str,
    topic: Optional[str] = None,
    difficulty: str = "medium",
    num_questions: int = 5
) -> Dict[str, Any]:
    """
    Generate a custom quiz using AI based on subject and topic.
    
    Args:
        subject: Subject area (MATHEMATICS, CHEMISTRY, etc.)
        topic: Specific topic (optional, will generate diverse questions if not provided)
        difficulty: Difficulty level (easy, medium, hard)
        num_questions: Number of questions to generate (1-10)
    
    Returns:
        Dictionary with quiz metadata and questions array
    """
    if not GEMINI_AVAILABLE or not model:
        raise Exception("AI service not available")
    
    # Validate inputs
    num_questions = max(1, min(num_questions, 10))
    difficulty = difficulty.lower() if difficulty.lower() in ['easy', 'medium', 'hard'] else 'medium'
    
    # Build quiz generation prompt
    quiz_prompt = f"""Generate a {difficulty} level quiz for {subject}."""
    
    if topic:
        quiz_prompt += f" Focus on the topic: {topic}."
    
    quiz_prompt += f"""

Generate exactly {num_questions} multiple choice questions. Each question must have:
- A clear question text with proper LaTeX formatting for any math (use $formula$ syntax)
- Exactly 4 answer options (A, B, C, D)
- One correct answer
- A detailed explanation of why the answer is correct

Format your response as a JSON object with this structure:
{{
    "title": "Quiz title",
    "subject": "{subject}",
    "topic": "{topic or 'General'}",
    "difficulty": "{difficulty}",
    "questions": [
        {{
            "question": "Question text with $LaTeX$ if needed",
            "options": {{
                "A": "First option",
                "B": "Second option",
                "C": "Third option",
                "D": "Fourth option"
            }},
            "correct_answer": "A",
            "explanation": "Detailed explanation with steps"
        }}
    ]
}}

IMPORTANT LATEX RULES:
- Use $formula$ for inline math, $$formula$$ for display math
- Use \\\\frac{{num}}{{den}} for fractions (double backslash)
- Use \\\\text{{word}} for text in formulas
- Escape all backslashes properly

Make questions relevant to WAEC exam format and West African curriculum."""

    try:
        response = model.generate_content(quiz_prompt)
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*$', '', response_text)
        
        # Parse JSON
        quiz_data = json.loads(response_text)
        
        # Validate structure
        if 'questions' not in quiz_data or not isinstance(quiz_data['questions'], list):
            raise ValueError("Invalid quiz format: missing questions array")
        
        # Add metadata
        quiz_data.setdefault('title', f"{subject} Quiz")
        quiz_data.setdefault('subject', subject)
        quiz_data.setdefault('topic', topic or 'General')
        quiz_data.setdefault('difficulty', difficulty)
        quiz_data['num_questions'] = len(quiz_data['questions'])
        
        logger.info(f"Generated {len(quiz_data['questions'])} question quiz for {subject}")
        
        return quiz_data
    
    except json.JSONDecodeError as e:
        logger.error(f"Quiz JSON parsing failed: {str(e)}")
        logger.error(f"Response text: {response_text[:500]}")
        raise Exception(f"Failed to parse AI quiz response: {str(e)}")
    except Exception as e:
        logger.error(f"Quiz generation failed: {str(e)}")
        raise Exception(f"Quiz generation failed: {str(e)}")


async def generate_ai_recommendations(
    performance_data: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Generate personalized study recommendations using AI.
    
    Args:
        performance_data: Dictionary containing student performance metrics
        
    Returns:
        List of recommendation objects
    """
    if not GEMINI_AVAILABLE or not model:
        return []

    prompt = f"""
    As an expert WAEC tutor, analyze this student's performance data and provide 3-4 highly personalized study recommendations.
    
    Student Performance Data:
    {json.dumps(performance_data, indent=2)}
    
    For each recommendation, provide:
    1. A catchy title
    2. A supportive and actionable message (max 150 chars)
    3. Priority (high, medium, low)
    4. Type (weak_topics, consistency, exam_readiness, coverage)
    5. Action (e.g., "practice_topics", "start_review", "take_quiz")
    
    Format your response as a JSON array of objects:
    [
        {{
            "title": "Title",
            "message": "Actionable advice...",
            "priority": "high",
            "type": "weak_topics",
            "action": "practice_topics",
            "data": {{}}
        }}
    ]
    
    Keep the tone encouraging and focused on West African curriculum (WAEC/WASSCE).
    """

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean JSON response
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*$', '', response_text)
        
        recommendations = json.loads(response_text)
        return recommendations
    except Exception as e:
        logger.error(f"AI recommendation generation failed: {e}")
        return []


def check_ai_quota(db: Session, user_id: int) -> bool:
    """
    Check if user has remaining AI quota.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    
    # If limit is -1, it's unlimited
    if user.ai_quota_limit == -1:
        return True
        
    return user.ai_quota_used < user.ai_quota_limit


def increment_ai_usage(db: Session, user_id: int, request_type: str = "explanation"):
    """
    Track AI usage for quota management.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.ai_quota_used += 1
        db.commit()


def get_ai_quota_status(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Get the current quota status for a user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"limit": 0, "used": 0, "remaining": 0}
        
    remaining = max(0, user.ai_quota_limit - user.ai_quota_used) if user.ai_quota_limit != -1 else 9999
    
    return {
        "limit": user.ai_quota_limit,
        "used": user.ai_quota_used,
        "remaining": remaining,
        "is_unlimited": user.ai_quota_limit == -1
    }
