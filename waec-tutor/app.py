from flask import Flask, render_template, request, jsonify, send_from_directory
from services.ai_engine import get_ai_response, clean_for_speech, generate_quiz_json
from app_strategic_additions import register_strategic_endpoints

app = Flask(__name__)

# Register strategic endpoints (AI, Assets, Billing)
register_strategic_endpoints(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('static', 'service-worker.js')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    history = data.get('history', [])
    subject = data.get('subject', 'General')
    socratic_mode = data.get('socratic_mode', False)  # NEW: Socratic toggle
    
    if history:
        history[-1]['content'] = f"(Current Subject: {subject}) {history[-1]['content']}"

    result = get_ai_response(history, subject, socratic_mode=socratic_mode)
    
    return jsonify({
        "response": result.get("text", ""),
        "voice_text": clean_for_speech(result.get("text", "")),
        "action": result.get("action"),
        "action_subject": result.get("action_subject"),
        "action_topic": result.get("action_topic") # <--- NEW
    })

@app.route('/api/quiz', methods=['POST'])
def quiz():
    subject = request.json.get('subject')
    topic = request.json.get('topic', 'General')
    difficulty = request.json.get('difficulty', 'medium')
    question_count = request.json.get('question_count', 10)
    
    json_str = generate_quiz_json(subject, topic, difficulty, question_count)
    clean_json = json_str.replace("```json", "").replace("```", "").strip()
    return jsonify(clean_json)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
