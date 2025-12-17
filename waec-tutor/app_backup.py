import os
import logging
import time
import re
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
from google.generativeai.types import HarmCategory, HarmBlockThreshold

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

app = Flask(__name__)

# --- CONFIGURATION ---
MODEL_FALLBACK_LIST = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-flash-lite-latest", "gemini-1.5-flash-latest"]

safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# UPDATED PROMPT: Forces LaTeX output
SYSTEM_INSTRUCTION = """
You are "Base10", an expert WAEC Tutor.
1. CONTEXT: Maintain the flow of the conversation. If we are doing Indices, stay on Indices.
2. FORMAT: 
   - Use Markdown for text.
   - Use LaTeX for ALL math formulas wrapped in double dollar signs. 
   - Example: $$ x^2 + \\frac{1}{2} $$
   - Do NOT use code blocks for math.
3. EXPLANATIONS: Be step-by-step and encouraging.
"""

# --- NEW: ADVANCED CLEANER FOR LATEX ---
def clean_for_speech(text):
    # 1. Clean Markdown headers/bold
    text = re.sub(r'#+\s?|(\*\*|__)', '', text)
    
    # 2. Convert common LaTeX patterns to English
    # Remove the $$ wrappers
    text = text.replace('$$', '')
    text = text.replace('$', '')
    
    # Fractions: \frac{a}{b} -> a over b
    text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\1 over \2', text)
    
    # Powers: x^2 -> x squared, x^3 -> x cubed, x^{n} -> x to the power of n
    text = text.replace('^2', ' squared ')
    text = text.replace('^3', ' cubed ')
    text = re.sub(r'\^\{?([^}]+)\}?', r' to the power of \1', text)
    
    # Symbols
    text = text.replace('\\times', ' times ')
    text = text.replace('\\div', ' divided by ')
    text = text.replace('\\pm', ' plus or minus ')
    text = text.replace('\\sqrt', ' square root ')
    text = text.replace('\\approx', ' is approximately ')
    text = text.replace('\\neq', ' is not equal to ')
    text = text.replace('\\le', ' is less than or equal to ')
    text = text.replace('\\ge', ' is greater than or equal to ')
    
    # Cleanup extra backslashes and LaTeX garbage
    text = text.replace('\\', '') 
    text = text.replace('{', '').replace('}', '') # Remove brackets
    
    return text.strip()

def generate_response(messages):
    """Sends the whole history to the model"""
    try:
        model_name = MODEL_FALLBACK_LIST[0] # Using best available
        model = genai.GenerativeModel(model_name, system_instruction=SYSTEM_INSTRUCTION)
        
        # Convert frontend history format to Gemini format
        # Gemini expects: [{'role': 'user', 'parts': ['...']}, {'role': 'model', 'parts': ['...']}]
        gemini_history = []
        for msg in messages:
            role = "user" if msg['role'] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg['content']]})
            
        # We use chat session logic for context
        chat = model.start_chat(history=gemini_history[:-1]) # Load history except last message
        last_message = gemini_history[-1]['parts'][0]
        
        response = chat.send_message(last_message, safety_settings=safety_settings)
        return response.text
    except Exception as e:
        logger.error(f"Error: {e}")
        return "I'm having trouble connecting. Please try again."

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    # Receive the full history from frontend
    history = data.get('history', []) 
    subject = data.get('subject', 'General')
    
    # Add the subject context to the last message invisible to user
    # This helps keep the AI focused even if the history is long
    last_user_msg = history[-1]['content']
    history[-1]['content'] = f"(Context: Subject is {subject}) {last_user_msg}"

    ai_text = generate_response(history)
    voice_clean = clean_for_speech(ai_text)
    
    return jsonify({"response": ai_text, "voice_text": voice_clean})

@app.route('/api/generate_quiz', methods=['POST'])
def generate_quiz():
    # Keep quiz logic simple/stateless for now
    subject = request.json.get('subject')
    model = genai.GenerativeModel(MODEL_FALLBACK_LIST[0])
    prompt = f"Create a JSON object with 3 WAEC multiple choice questions for {subject}. Format: {{ 'questions': [ {{ 'q': '...', 'options': ['A', 'B', 'C', 'D'], 'answer': 'A' }} ] }}"
    res = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
    return jsonify(res.text)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
