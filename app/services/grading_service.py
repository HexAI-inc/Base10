"""AI-assisted grading service."""
from typing import Dict
from app.services.ai_service import model, GEMINI_AVAILABLE
import json


async def auto_grade_submission(question_text: str, marking_scheme: str, student_answer: str) -> Dict:
    """Call the AI model to suggest a score and feedback.

    Returns: {"score": int, "feedback": str}
    """
    if not GEMINI_AVAILABLE or not model:
        return {"score": 0, "feedback": "AI grading not available"}

    prompt = f"""
You are a strict but fair WAEC-style teacher grading a student's short essay/answer.

Question: {question_text}
Marking Scheme / Key Points: {marking_scheme}
Student Answer: {student_answer}

Task:
1) Assign a score from 0 to 100 based on how well the student covered the marking scheme.
2) Provide brief constructive feedback (one or two sentences).

Output strictly as JSON: {{"score": int, "feedback": "string"}}
"""
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Try to parse JSON from response
        try:
            data = json.loads(text)
            score = int(data.get("score", 0))
            feedback = data.get("feedback", "")
            return {"score": score, "feedback": feedback}
        except Exception:
            # Fallback parsing: look for numbers
            return {"score": 0, "feedback": text}
    except Exception as e:
        return {"score": 0, "feedback": f"AI grading failed: {str(e)}"}