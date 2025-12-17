import os
import re
import logging
import time
import json
import google.generativeai as genai
from dotenv import load_dotenv
from services.quiz_service import get_static_quiz, format_questions

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

logger = logging.getLogger(__name__)

MODEL_LIST = ["gemma-3-12b-it", "gemini-2.0-flash-lite-preview-02-05", "gemini-flash-latest"]

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
   - NEVER use \\rightarrow, \\leftarrow, \\to in JSON - use → or ← or words like "produces", "yields"
   - Example: "The mass is 5 kg and energy is $E = \\frac{1}{2}mv^2$"
   - Example: "$HCl + NaOH$ produces $NaCl + H_2O$" (not \\rightarrow)
3. CONTEXT AWARENESS: Pay attention to the subject and topic being discussed.
4. MODES:
   - CHAT MODE (default): When user asks for help, explanation, "how to", "solve this", or "explain" - EXPLAIN thoroughly and accurately.
   - QUIZ MODE: ONLY when user explicitly asks for "quiz", "test", "practice questions", or "exercises".
   - TRIGGER: If Quiz Mode is active, output: [QUIZ_MODE: Subject | Topic]
     * Extract the SPECIFIC subject (e.g., English Language, Mathematics, Physics, Chemistry)
     * Extract the SPECIFIC topic from the conversation (e.g., adjectives, specific heat capacity, equilibrium)
     * Examples:
       - "give me a quiz on adjectives" → [QUIZ_MODE: English Language | adjectives]
       - "test me on specific heat capacity" → [QUIZ_MODE: Physics | specific heat capacity]
       - "practice equilibrium" → [QUIZ_MODE: Chemistry | equilibrium]

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

Bad (Direct Answer):
User: "Calculate the specific heat capacity"
AI: "Q = mcΔT, so c = Q/(mΔT) = 500"

Good (Socratic):
User: "Calculate the specific heat capacity"
AI: "Let's break this down step by step. First, can you identify which formula relates heat energy (Q), mass (m), temperature change (ΔT), and specific heat capacity (c)?"

MATH/SCIENCE NOTATION (same as default):
   - Use LaTeX for formulas: $E = mc^2$
   - Plain text for units: kg, K, J
   - NEVER use \\text{} or \\rightarrow

6. STAY ON TOPIC: Focus on the current subject.
"""

def clean_for_speech(text):
    text = re.sub(r'\[QUIZ_MODE:.*?\]', '', text)
    text = re.sub(r'<[^>]+>', '', text) 
    text = re.sub(r'#+', '', text)
    text = re.sub(r'\*\*|__', '', text)
    replacements = [
        (r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\1 over \2'),
        (r'\^\{?2\}?', ' squared'),
        (r'\^\{?3\}?', ' cubed'),
        (r'\\times', ' times '),
        (r'\$', ''), 
    ]
    for pattern, word in replacements:
        text = re.sub(pattern, word, text)
    return re.sub(r'[^a-zA-Z0-9\s.,?!]', ' ', text).strip()

def sanitize_json_output(text):
    """
    Sanitizes JSON from LLMs, properly escaping LaTeX commands.
    """
    text = text.replace("```json", "").replace("```", "").strip()
    
    # Parse JSON first to get the actual structure
    try:
        # Try parsing as-is first
        data = json.loads(text)
        
        # If successful, recursively fix LaTeX in all strings
        def fix_latex_in_value(val):
            if isinstance(val, str):
                # Replace single backslash with double backslash for LaTeX commands
                # But be careful not to affect already-escaped backslashes
                val = re.sub(r'\\(?!\\)', r'\\\\', val)
                return val
            elif isinstance(val, dict):
                return {k: fix_latex_in_value(v) for k, v in val.items()}
            elif isinstance(val, list):
                return [fix_latex_in_value(item) for item in val]
            return val
        
        fixed_data = fix_latex_in_value(data)
        return json.dumps(fixed_data)
        
    except json.JSONDecodeError:
        # If parsing fails, do manual fixes before parsing
        # Replace common broken LaTeX patterns
        replacements = [
            (r'\\frac', r'\\\\frac'),
            (r'\\sqrt', r'\\\\sqrt'),
            (r'\\times', r'\\\\times'),
            (r'\\div', r'\\\\div'),
            (r'\\cdot', r'\\\\cdot'),
            (r'\\theta', r'\\\\theta'),
            (r'\\alpha', r'\\\\alpha'),
            (r'\\beta', r'\\\\beta'),
            (r'\\pi', r'\\\\pi'),
            (r'\\sum', r'\\\\sum'),
            (r'\\int', r'\\\\int'),
            (r'\\pm', r'\\\\pm'),
            (r'\\leq', r'\\\\leq'),
            (r'\\geq', r'\\\\geq'),
            (r'\\neq', r'\\\\neq'),
        ]
        
        for pattern, replacement in replacements:
            # Only replace if not already double-escaped
            text = re.sub(pattern + r'(?!\\)', replacement, text)
        
        # Try parsing again
        try:
            data = json.loads(text)
            return json.dumps(data)
        except:
            # Last resort - return as is
            return text

def get_ai_response(history, subject="General", socratic_mode=False):
    """
    Generate AI response with optional Socratic teaching mode.
    
    Args:
        history: Conversation history
        subject: Current subject context
        socratic_mode: If True, use Socratic prompting to guide learning instead of giving answers
    """
    # Choose prompt based on mode
    system_prompt = SOCRATIC_PROMPT if socratic_mode else SYSTEM_PROMPT
    
    gemini_history = []
    for msg in history:
        role = "user" if msg['role'] == "user" else "model"
        if msg.get('content'):
            gemini_history.append({"role": role, "parts": [msg['content']]})

    for model_name in MODEL_LIST:
        try:
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            
            if "gemma" in model_name.lower():
                model = genai.GenerativeModel(model_name, generation_config=generation_config)
                if gemini_history and "You are" not in gemini_history[0]['parts'][0]:
                    gemini_history[0]['parts'][0] = f"{system_prompt}\n\n{gemini_history[0]['parts'][0]}"
            else:
                model = genai.GenerativeModel(
                    model_name, 
                    system_instruction=system_prompt,
                    generation_config=generation_config
                )

            chat = model.start_chat(history=gemini_history[:-1])
            response = chat.send_message(gemini_history[-1]['parts'][0])
            text = response.text
            
            action = None
            action_subject = None
            action_topic = None
            
            match = re.search(r'\[QUIZ_MODE:\s*(.*?)\s*\|\s*(.*?)\]', text)
            if match:
                action = "trigger_quiz"
                action_subject = match.group(1).strip()
                action_topic = match.group(2).strip()
                text = f"Starting {action_subject} Quiz ({action_topic})..."

            return {"type": "text", "text": text, "action": action, "action_subject": action_subject, "action_topic": action_topic}

        except Exception as e:
            time.sleep(1)
            
    return {"type": "text", "text": "Connection issue."}

def generate_quiz_json(subject, topic=None, difficulty="medium", question_count=10):
    from services.quiz_service import get_static_quiz
    
    topic_str = f"specifically on the topic of '{topic}'" if topic and topic != "General" else "covering general knowledge"
    
    # Map difficulty to question complexity
    difficulty_instructions = {
        "easy": "Create simple, straightforward questions suitable for beginners. Focus on basic concepts and direct recall.",
        "medium": "Create moderate difficulty questions that test understanding and application of concepts.",
        "hard": "Create challenging questions that require deep understanding, analysis, and problem-solving skills."
    }
    
    difficulty_desc = difficulty_instructions.get(difficulty, difficulty_instructions["medium"])
    
    for model_name in MODEL_LIST:
        try:
            model = genai.GenerativeModel(
                model_name,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                }
            )
            
            prompt = f"""
You are creating a WAEC exam quiz {topic_str} for {subject}.

CRITICAL REQUIREMENTS:
1. ALL questions MUST be strictly about: {topic if topic else subject}
2. DO NOT include questions about other topics
3. Be factually accurate - only use well-established concepts from WAEC curriculum
4. {difficulty_desc}

LATEX FORMATTING RULES (VERY IMPORTANT):
- Wrap ALL math/science notation in $ signs
- Use plain text for units: kg, K, J (NOT \\text{{kg}})
- For fractions: $\\frac{{a}}{{b}}$
- For powers: $x^2$ or $x^{{10}}$
- For subscripts: $c_p$ or $T_1$
- For Greek letters: $\\theta$, $\\Delta$
- Example: "2.0 kg" NOT "$2.0\\text{{kg}}$"
- Example: "$Q = mc\\Delta T$" where Q, m, c are variables
- DO NOT use \\text{{}} command - it breaks rendering

Create exactly {question_count} questions in this EXACT JSON format:
[
  {{
    "id": 1,
    "question": "Question text here with 5 kg mass",
    "options": ["A. First option with $\\frac{{1}}{{2}}$", "B. Second option", "C. Third option", "D. Fourth option"],
    "answer": "A",
    "explanation": "Brief explanation"
  }}
]

Each question MUST:
- Be about {topic if topic else subject} ONLY
- Have exactly 4 options (A, B, C, D)
- Use proper LaTeX WITHOUT \\text{{}} commands
- Have one correct answer
"""
            try:
                res = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            except:
                res = model.generate_content(prompt)
            
            clean_text = sanitize_json_output(res.text)
            
            if "[" in clean_text and "]" in clean_text:
                raw_list = json.loads(clean_text)
                
                # Clean up any \text{} commands that break rendering
                def clean_latex(text):
                    if not isinstance(text, str):
                        return text
                    # Remove \text{} wrappers, keep the content
                    text = re.sub(r'\\text\{([^}]+)\}', r'\1', text)
                    # Remove \mathrm{} wrappers
                    text = re.sub(r'\\mathrm\{([^}]+)\}', r'\1', text)
                    return text
                
                # Apply cleaning to all text fields
                for q in raw_list:
                    if 'question' in q:
                        q['question'] = clean_latex(q['question'])
                    if 'options' in q:
                        q['options'] = [clean_latex(opt) for opt in q['options']]
                    if 'explanation' in q:
                        q['explanation'] = clean_latex(q['explanation'])
                
                final_list = format_questions(raw_list)
                return json.dumps({"questions": final_list})
        except Exception as e:
            logger.error(f"Quiz Error with {model_name}: {e}")
            continue
    
    # Fallback to static quiz from JSON file with topic search
    logger.info(f"Falling back to static quiz: subject={subject}, topic={topic}")
    return get_static_quiz(subject, topic, question_count)
