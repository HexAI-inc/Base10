"""
Teacher AI Assistant - Natural language interface for classroom management.

Helps teachers:
- Create quizzes and assignments
- Get student performance insights
- Identify struggling students
- Generate reports
- Manage classroom activities
"""
import google.generativeai as genai
import json
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case

from app.core.config import settings
from app.models.user import User
from app.models.classroom import Classroom, Assignment
from app.models.question import Question
from app.models.progress import Attempt
from app.models.enums import Subject, Topic, DifficultyLevel, GradeLevel

logger = logging.getLogger(__name__)

# Configure Gemini
try:
    GOOGLE_API_KEY = getattr(settings, 'GOOGLE_API_KEY', '')
    if GOOGLE_API_KEY:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        GEMINI_AVAILABLE = True
        logger.info("✅ Teacher AI Assistant initialized")
    else:
        GEMINI_AVAILABLE = False
        model = None
        logger.warning("⚠️ Google API key not found - AI Assistant disabled")
except Exception as e:
    logger.error(f"Failed to configure Teacher AI Assistant: {e}")
    GEMINI_AVAILABLE = False
    model = None


SYSTEM_PROMPT = """
You are an AI teaching assistant for Base10, helping teachers manage their classrooms efficiently.

Your capabilities:
1. CREATE QUIZ - Generate quizzes on specific topics
2. ANALYZE PERFORMANCE - Provide insights on student performance
3. IDENTIFY STRUGGLING STUDENTS - Find students who need help
4. SUGGEST INTERVENTIONS - Recommend teaching strategies
5. GENERATE REPORTS - Create summaries of classroom activity

When a teacher makes a request, analyze their intent and respond with a structured action plan.

RESPONSE FORMAT:
You must respond with valid JSON in this exact structure:
{
  "intent": "create_quiz|analyze_performance|identify_struggling|generate_report|general_query",
  "confidence": 0.0-1.0,
  "parameters": {
    "classroom_id": int or null,
    "subject": "Mathematics|Physics|..." or null,
    "topic": "Algebra|..." or null,
    "grade_level": "JSS1|SS3|..." or null,
    "question_count": int or null,
    "difficulty": "easy|medium|hard" or null,
    "time_period": "last_week|last_month|all_time" or null
  },
  "action_summary": "Brief summary of what will be done",
  "requires_approval": true|false,
  "questions_to_clarify": ["question1", "question2"] or []
}

EXAMPLES:

Teacher: "Create a quiz on Quadratic Equations for my SS2 class with 10 questions"
Response:
{
  "intent": "create_quiz",
  "confidence": 0.95,
  "parameters": {
    "subject": "Mathematics",
    "topic": "Quadratic Equations",
    "grade_level": "SS2",
    "question_count": 10,
    "difficulty": "medium"
  },
  "action_summary": "I'll create a 10-question quiz on Quadratic Equations for SS2 students at medium difficulty",
  "requires_approval": true,
  "questions_to_clarify": []
}

Teacher: "Which students are struggling in my Physics class?"
Response:
{
  "intent": "identify_struggling",
  "confidence": 0.90,
  "parameters": {
    "subject": "Physics",
    "time_period": "last_week"
  },
  "action_summary": "I'll analyze recent performance data to identify Physics students who may need extra support",
  "requires_approval": false,
  "questions_to_clarify": ["Which specific classroom? Please provide the classroom ID or name"]
}

Teacher: "Give me a summary of how my class performed this week"
Response:
{
  "intent": "generate_report",
  "confidence": 0.85,
  "parameters": {
    "time_period": "last_week"
  },
  "action_summary": "I'll generate a weekly performance summary for your classroom",
  "requires_approval": false,
  "questions_to_clarify": ["Which classroom would you like the report for?"]
}

Always respond with valid JSON. Be helpful and educational.
"""


class TeacherAIAssistant:
    """AI-powered assistant for teachers."""
    
    def __init__(self, db: Session, teacher: User):
        self.db = db
        self.teacher = teacher
        self.model = model
        self.available = GEMINI_AVAILABLE
    
    async def process_request(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process natural language request from teacher.
        
        Args:
            message: Teacher's natural language request
            context: Optional context (classroom_id, previous conversation, etc.)
        
        Returns:
            Structured response with action plan
        """
        if not self.available:
            return {
                "error": "AI Assistant is currently unavailable",
                "message": "Please try again later or contact support"
            }
        
        # Get teacher's classrooms for context
        classrooms = self.db.query(Classroom).filter(
            Classroom.teacher_id == self.teacher.id
        ).all()
        
        classroom_info = "\n".join([
            f"- {c.name} (ID: {c.id}, Subject: {c.subject}, Grade: {c.grade_level})"
            for c in classrooms
        ])
        
        # Build enhanced prompt with context
        enhanced_prompt = f"""{SYSTEM_PROMPT}

TEACHER'S CLASSROOMS:
{classroom_info if classroom_info else "No classrooms yet"}

CONTEXT:
{json.dumps(context, indent=2) if context else "No additional context"}

TEACHER'S REQUEST:
"{message}"

Analyze the request and respond with valid JSON following the exact format specified above.
"""
        
        try:
            response = self.model.generate_content(enhanced_prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
            
            # Parse JSON
            parsed_response = json.loads(response_text)
            
            # Execute action based on intent
            intent = parsed_response.get('intent')
            parameters = parsed_response.get('parameters', {})
            
            if intent == 'create_quiz':
                quiz_data = await self._create_quiz(parameters)
                parsed_response['quiz_data'] = quiz_data
            
            elif intent == 'analyze_performance':
                analysis = await self._analyze_performance(parameters)
                parsed_response['analysis'] = analysis
            
            elif intent == 'identify_struggling':
                struggling_students = await self._identify_struggling_students(parameters)
                parsed_response['struggling_students'] = struggling_students
            
            elif intent == 'generate_report':
                report = await self._generate_report(parameters)
                parsed_response['report'] = report
            
            return parsed_response
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            return {
                "error": "Failed to understand request",
                "message": "Please rephrase your request more clearly",
                "raw_response": response_text if 'response_text' in locals() else None
            }
        except Exception as e:
            logger.error(f"Error processing teacher request: {e}")
            return {
                "error": "An error occurred",
                "message": str(e)
            }
    
    async def _create_quiz(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate quiz questions based on parameters.
        
        Returns draft questions for teacher review.
        """
        subject = parameters.get('subject')
        topic = parameters.get('topic')
        grade_level = parameters.get('grade_level')
        question_count = parameters.get('question_count', 10)
        difficulty = parameters.get('difficulty', 'medium')
        
        # Query existing questions from database
        query = self.db.query(Question).filter(Question.deleted_at == None)
        
        if subject:
            try:
                query = query.filter(Question.subject == Subject(subject))
            except ValueError:
                pass
        
        if topic:
            try:
                query = query.filter(Question.topic == Topic(topic))
            except ValueError:
                pass
        
        if difficulty:
            try:
                query = query.filter(Question.difficulty == DifficultyLevel(difficulty))
            except ValueError:
                pass
        
        # Get random questions
        questions = query.order_by(func.random()).limit(question_count).all()
        
        quiz_questions = []
        for q in questions:
            options = json.loads(q.options_json) if q.options_json else []
            quiz_questions.append({
                'id': q.id,
                'content': q.content,
                'options': options,
                'correct_index': q.correct_index,
                'explanation': q.explanation,
                'subject': q.subject.value if q.subject else None,
                'topic': q.topic.value if q.topic else None,
                'difficulty': q.difficulty.value if q.difficulty else None
            })
        
        return {
            'questions': quiz_questions,
            'total_found': len(quiz_questions),
            'requested': question_count,
            'source': 'database',
            'parameters': parameters
        }
    
    async def _analyze_performance(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze classroom or student performance.
        """
        classroom_id = parameters.get('classroom_id')
        time_period = parameters.get('time_period', 'last_week')
        
        if not classroom_id:
            return {
                'error': 'Classroom ID required for performance analysis'
            }
        
        # Verify classroom ownership
        classroom = self.db.query(Classroom).filter(
            Classroom.id == classroom_id,
            Classroom.teacher_id == self.teacher.id
        ).first()
        
        if not classroom:
            return {
                'error': 'Classroom not found or access denied'
            }
        
        # Get time range
        if time_period == 'last_week':
            start_date = datetime.utcnow() - timedelta(days=7)
        elif time_period == 'last_month':
            start_date = datetime.utcnow() - timedelta(days=30)
        else:
            start_date = None
        
        # Get student IDs
        student_ids = [s.id for s in classroom.students]
        
        if not student_ids:
            return {
                'message': 'No students in this classroom yet',
                'classroom_name': classroom.name
            }
        
        # Query attempts
        query = self.db.query(Attempt).filter(Attempt.user_id.in_(student_ids))
        if start_date:
            query = query.filter(Attempt.attempted_at >= start_date)
        
        attempts = query.all()
        
        if not attempts:
            return {
                'message': 'No activity recorded in this period',
                'classroom_name': classroom.name,
                'time_period': time_period
            }
        
        # Calculate metrics
        total_attempts = len(attempts)
        correct_attempts = sum(1 for a in attempts if a.is_correct)
        accuracy = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
        
        # Psychometric analysis
        times = [a.time_taken_ms for a in attempts if a.time_taken_ms]
        avg_time = sum(times) / len(times) if times else None
        
        guesses = sum(1 for a in attempts if a.time_taken_ms and a.time_taken_ms < 2000)
        guessing_rate = (guesses / total_attempts * 100) if total_attempts > 0 else 0
        
        struggles = sum(1 for a in attempts if a.time_taken_ms and a.time_taken_ms > 60000)
        struggle_rate = (struggles / total_attempts * 100) if total_attempts > 0 else 0
        
        # Active students
        active_students = len(set(a.user_id for a in attempts))
        
        return {
            'classroom_name': classroom.name,
            'time_period': time_period,
            'total_students': len(student_ids),
            'active_students': active_students,
            'total_attempts': total_attempts,
            'accuracy': round(accuracy, 2),
            'avg_time_seconds': round(avg_time / 1000, 2) if avg_time else None,
            'guessing_rate': round(guessing_rate, 2),
            'struggle_rate': round(struggle_rate, 2),
            'insights': self._generate_insights(accuracy, guessing_rate, struggle_rate, active_students, len(student_ids))
        }
    
    async def _identify_struggling_students(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify students who need help.
        """
        classroom_id = parameters.get('classroom_id')
        subject = parameters.get('subject')
        
        if not classroom_id:
            return {'error': 'Classroom ID required'}
        
        classroom = self.db.query(Classroom).filter(
            Classroom.id == classroom_id,
            Classroom.teacher_id == self.teacher.id
        ).first()
        
        if not classroom:
            return {'error': 'Classroom not found'}
        
        student_ids = [s.id for s in classroom.students]
        struggling_students = []
        
        for student_id in student_ids:
            user = self.db.query(User).filter(User.id == student_id).first()
            attempts = self.db.query(Attempt).filter(Attempt.user_id == student_id).all()
            
            if not attempts:
                continue
            
            total = len(attempts)
            correct = sum(1 for a in attempts if a.is_correct)
            accuracy = (correct / total * 100) if total > 0 else 0
            
            # Identify struggling: accuracy < 50% or high misconception rate
            misconceptions = sum(
                1 for a in attempts
                if a.confidence_level and a.confidence_level >= 4 and not a.is_correct
            )
            misconception_rate = (misconceptions / total * 100) if total > 0 else 0
            
            if accuracy < 50 or misconception_rate > 20:
                struggling_students.append({
                    'student_id': student_id,
                    'student_name': user.full_name or 'Unknown',
                    'accuracy': round(accuracy, 2),
                    'total_attempts': total,
                    'misconception_rate': round(misconception_rate, 2),
                    'needs_help_with': 'fundamental concepts' if accuracy < 50 else 'correcting misconceptions'
                })
        
        return {
            'classroom_name': classroom.name,
            'total_students': len(student_ids),
            'struggling_count': len(struggling_students),
            'students': struggling_students,
            'recommendations': self._generate_recommendations(struggling_students)
        }
    
    async def _generate_report(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive classroom report.
        """
        classroom_id = parameters.get('classroom_id')
        time_period = parameters.get('time_period', 'last_week')
        
        if not classroom_id:
            return {'error': 'Classroom ID required'}
        
        # Get performance analysis
        performance = await self._analyze_performance({'classroom_id': classroom_id, 'time_period': time_period})
        
        # Get struggling students
        struggling = await self._identify_struggling_students({'classroom_id': classroom_id})
        
        # Generate AI summary
        summary_prompt = f"""
As an educational analyst, provide a concise summary (3-4 sentences) of this classroom's performance:

Performance Data:
- Total attempts: {performance.get('total_attempts', 0)}
- Accuracy: {performance.get('accuracy', 0)}%
- Active students: {performance.get('active_students', 0)} / {performance.get('total_students', 0)}
- Guessing rate: {performance.get('guessing_rate', 0)}%
- Struggle rate: {performance.get('struggle_rate', 0)}%

Struggling Students: {struggling.get('struggling_count', 0)}

Provide encouraging but honest feedback with specific action items.
"""
        
        try:
            summary_response = self.model.generate_content(summary_prompt)
            ai_summary = summary_response.text.strip()
        except:
            ai_summary = "Performance analysis complete. Review detailed metrics below."
        
        return {
            'summary': ai_summary,
            'performance_metrics': performance,
            'struggling_students': struggling,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def _generate_insights(self, accuracy: float, guessing_rate: float, struggle_rate: float, 
                          active_students: int, total_students: int) -> List[str]:
        """Generate actionable insights from metrics."""
        insights = []
        
        if accuracy < 50:
            insights.append("⚠️ Low accuracy suggests fundamental concepts need reinforcement")
        elif accuracy < 70:
            insights.append("📊 Moderate performance - students need more practice")
        else:
            insights.append("✅ Strong performance - students are grasping concepts well")
        
        if guessing_rate > 30:
            insights.append("🎲 High guessing rate - students may need more time per question")
        
        if struggle_rate > 20:
            insights.append("😓 Many students struggling - consider breaking topics into smaller chunks")
        
        engagement = (active_students / total_students * 100) if total_students > 0 else 0
        if engagement < 50:
            insights.append("📉 Low engagement - try gamification or group activities")
        
        return insights
    
    def _generate_recommendations(self, struggling_students: List[Dict]) -> List[str]:
        """Generate teaching recommendations based on struggling students."""
        if not struggling_students:
            return ["✅ All students performing well - maintain current teaching approach"]
        
        recommendations = []
        
        if len(struggling_students) > 5:
            recommendations.append("Consider dedicating a review session for the entire class")
        else:
            recommendations.append("Provide one-on-one or small group tutoring for struggling students")
        
        # Check for misconceptions
        high_misconception_students = [s for s in struggling_students if s.get('misconception_rate', 0) > 20]
        if high_misconception_students:
            recommendations.append("Address common misconceptions through targeted examples and discussions")
        
        recommendations.append("Assign practice exercises focusing on weak areas")
        recommendations.append("Use AI tutor to provide personalized explanations")
        
        return recommendations


async def process_teacher_command(
    db: Session,
    teacher: User,
    message: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Main entry point for teacher AI assistant.
    
    Args:
        db: Database session
        teacher: Teacher user object
        message: Natural language command
        context: Optional context (classroom_id, etc.)
    
    Returns:
        Structured response with action plan and data
    """
    assistant = TeacherAIAssistant(db, teacher)
    return await assistant.process_request(message, context)
