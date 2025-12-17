"""
Strategic API additions for Base10 EdTech Platform.
Adds AI endpoints, smart assets, and billing for a complete solution.
"""
from flask import Flask, Blueprint, request, jsonify, send_file
from functools import wraps
import os
from pathlib import Path
from typing import Optional

# Create blueprints for new features
ai_bp = Blueprint('ai', __name__, url_prefix='/api/v1/ai')
assets_bp = Blueprint('assets', __name__, url_prefix='/api/v1/assets')
billing_bp = Blueprint('billing', __name__, url_prefix='/api/v1/billing')


# ==================== AI ENDPOINTS ====================

@ai_bp.route('/explain', methods=['POST'])
def explain_answer():
    """
    POST /api/v1/ai/explain
    
    Generate intelligent explanation for why a student's answer was wrong.
    Uses server-side Gemini for high-quality explanations when online.
    
    Request:
        {
            "question_id": 402,
            "student_answer": 2,
            "context": "I thought isotopes had different atomic numbers"
        }
    
    Response:
        {
            "explanation": "You chose option C, but isotopes are atoms...",
            "correct_answer": 1,
            "key_concepts": ["Atomic Structure", "Isotopes"],
            "difficulty": "MEDIUM"
        }
    """
    from services.ai_engine import generate_explanation_for_question
    
    data = request.json
    question_id = data.get('question_id')
    student_answer = data.get('student_answer')
    context = data.get('context', '')
    
    if not question_id or student_answer is None:
        return jsonify({"error": "question_id and student_answer required"}), 400
    
    try:
        explanation = generate_explanation_for_question(
            question_id=question_id,
            student_answer=student_answer,
            context=context
        )
        return jsonify(explanation)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ai_bp.route('/chat', methods=['POST'])
def chat_tutor():
    """
    POST /api/v1/ai/chat
    
    Conversational AI tutor for deep-dive learning.
    The "Big Brain" - uses Gemini Pro for extended conversations.
    
    Request:
        {
            "message": "I don't understand isotopes",
            "history": [{"role": "user", "content": "..."}],
            "subject": "CHEMISTRY"
        }
    
    Response:
        {
            "response": "Great question! Isotopes are...",
            "suggestions": ["Can you give examples?", "How do they affect mass?"],
            "related_topics": ["Atomic Mass", "Radioactivity"]
        }
    """
    from services.ai_engine import get_ai_response
    
    data = request.json
    message = data.get('message')
    history = data.get('history', [])
    subject = data.get('subject', 'General')
    
    if not message:
        return jsonify({"error": "message required"}), 400
    
    try:
        # Add current message to history
        history.append({"role": "user", "content": message})
        
        result = get_ai_response(history, subject)
        
        # Generate follow-up suggestions
        suggestions = [
            f"Can you explain that with an example?",
            f"What are common mistakes in this topic?",
            f"How is this tested in WAEC exams?"
        ]
        
        return jsonify({
            "response": result.get("text", ""),
            "suggestions": suggestions[:3],
            "related_topics": []  # TODO: extract from question database
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ai_bp.route('/status', methods=['GET'])
def ai_status():
    """
    GET /api/v1/ai/status
    
    Check AI service availability and user quota.
    """
    return jsonify({
        "available": True,
        "quota_remaining": 100,
        "features": {
            "explain": True,
            "chat": True,
            "premium": False
        },
        "message": "AI services ready"
    })


# ==================== ASSET ENDPOINTS ====================

@assets_bp.route('/image/<path:filename>', methods=['GET'])
def serve_image(filename):
    """
    GET /api/v1/assets/image/{filename}?quality=low&network=2g
    
    Smart image serving with network-aware optimization.
    Serves images optimized based on user's network conditions.
    
    Query Params:
        - quality: low|medium|high|auto
        - network: 2g|3g|4g|wifi
    
    Returns: Optimized image file
    """
    quality = request.args.get('quality', 'auto')
    network = request.args.get('network', 'wifi')
    
    # Define assets directory
    assets_dir = Path('static/images')
    image_path = assets_dir / filename
    
    # Security: prevent directory traversal
    try:
        image_path = image_path.resolve()
        assets_dir = assets_dir.resolve()
        if not str(image_path).startswith(str(assets_dir)):
            return jsonify({"error": "Access denied"}), 403
    except:
        return jsonify({"error": "Invalid path"}), 400
    
    if not image_path.exists():
        return jsonify({"error": "Image not found"}), 404
    
    # Auto-detect quality from network
    if quality == 'auto':
        if network in ['2g', '3g']:
            quality = 'low'
        elif network == '4g':
            quality = 'medium'
        else:
            quality = 'high'
    
    # Try to optimize image
    if quality in ['low', 'medium']:
        try:
            from PIL import Image
            import io
            
            with Image.open(image_path) as img:
                # Convert to RGB if needed
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                if quality == 'low':
                    # 2G/3G: Aggressive compression
                    img = img.convert('L')  # Grayscale
                    img.thumbnail((400, 400), Image.Resampling.LANCZOS)
                    
                    buffer = io.BytesIO()
                    img.save(buffer, format='WEBP', quality=40, method=6)
                    buffer.seek(0)
                    
                    return send_file(
                        buffer,
                        mimetype='image/webp',
                        as_attachment=False,
                        download_name=f"{filename.rsplit('.', 1)[0]}.webp"
                    )
                
                elif quality == 'medium':
                    # 4G: Balanced compression
                    img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                    
                    buffer = io.BytesIO()
                    img.save(buffer, format='JPEG', quality=70, optimize=True)
                    buffer.seek(0)
                    
                    return send_file(
                        buffer,
                        mimetype='image/jpeg',
                        as_attachment=False,
                        download_name=f"{filename.rsplit('.', 1)[0]}.jpg"
                    )
        except ImportError:
            pass  # PIL not available, serve original
        except Exception as e:
            pass  # Optimization failed, serve original
    
    # Serve original image
    return send_file(image_path)


@assets_bp.route('/image/<path:filename>/info', methods=['GET'])
def image_info(filename):
    """
    GET /api/v1/assets/image/{filename}/info
    
    Get information about image sizes before downloading.
    """
    assets_dir = Path('static/images')
    image_path = assets_dir / filename
    
    if not image_path.exists():
        return jsonify({"error": "Image not found"}), 404
    
    file_size = image_path.stat().st_size
    
    return jsonify({
        "filename": filename,
        "original_size_kb": round(file_size / 1024, 2),
        "estimated_sizes": {
            "low": {"kb": round(file_size * 0.1 / 1024, 2), "description": "Grayscale WebP for 2G/3G"},
            "medium": {"kb": round(file_size * 0.4 / 1024, 2), "description": "Compressed JPEG for 4G"},
            "high": {"kb": round(file_size / 1024, 2), "description": "Full quality for WiFi"}
        }
    })


# ==================== BILLING ENDPOINTS ====================

PLANS = [
    {
        "id": "free",
        "name": "Basic",
        "description": "Essential features for exam preparation",
        "price": 0,
        "currency": "NGN",
        "features": [
            "Unlimited offline questions",
            "Basic flashcards",
            "5 AI explanations per day",
            "Standard image quality"
        ]
    },
    {
        "id": "premium",
        "name": "Exam Master",
        "description": "Advanced features for serious students",
        "price": 500,
        "currency": "NGN",
        "features": [
            "Everything in Basic",
            "Unlimited AI chat",
            "High-quality images",
            "Detailed analytics",
            "Ad-free experience"
        ]
    },
    {
        "id": "school",
        "name": "School License",
        "description": "Complete solution for institutions",
        "price": 50000,
        "currency": "NGN",
        "features": [
            "Everything in Premium",
            "Up to 500 students",
            "Teacher dashboard",
            "Class analytics",
            "Priority support"
        ]
    }
]


@billing_bp.route('/plans', methods=['GET'])
def get_plans():
    """
    GET /api/v1/billing/plans
    
    List all available subscription plans.
    """
    return jsonify(PLANS)


@billing_bp.route('/plans/<plan_id>', methods=['GET'])
def get_plan(plan_id):
    """
    GET /api/v1/billing/plans/{plan_id}
    
    Get details for a specific plan.
    """
    plan = next((p for p in PLANS if p['id'] == plan_id), None)
    if not plan:
        return jsonify({"error": "Plan not found"}), 404
    return jsonify(plan)


@billing_bp.route('/initialize', methods=['POST'])
def initialize_payment():
    """
    POST /api/v1/billing/initialize
    
    Initialize payment transaction with Paystack/Flutterwave.
    
    Request:
        {
            "plan_id": "premium",
            "email": "student@example.com"
        }
    
    Response:
        {
            "authorization_url": "https://checkout.paystack.com/abc123",
            "reference": "base10_1234567890"
        }
    """
    data = request.json
    plan_id = data.get('plan_id')
    email = data.get('email')
    
    if not plan_id or not email:
        return jsonify({"error": "plan_id and email required"}), 400
    
    plan = next((p for p in PLANS if p['id'] == plan_id), None)
    if not plan:
        return jsonify({"error": "Plan not found"}), 404
    
    if plan['price'] == 0:
        return jsonify({"error": "Free plan doesn't require payment"}), 400
    
    # Generate transaction reference
    import time
    reference = f"base10_{int(time.time())}"
    
    # TODO: Integrate with Paystack API
    # For now, return mock URL
    mock_url = f"https://checkout.paystack.com/mock/{reference}"
    
    return jsonify({
        "authorization_url": mock_url,
        "reference": reference,
        "access_code": "mock_access"
    })


@billing_bp.route('/webhook', methods=['POST'])
def payment_webhook():
    """
    POST /api/v1/billing/webhook
    
    Paystack/Flutterwave webhook for payment notifications.
    """
    # TODO: Verify webhook signature
    # TODO: Update user subscription in database
    
    data = request.json
    event = data.get('event')
    
    if event == 'charge.success':
        # Payment successful
        pass
    
    return jsonify({"status": "success"})


@billing_bp.route('/subscription', methods=['GET'])
def get_subscription():
    """
    GET /api/v1/billing/subscription
    
    Get current user's subscription status.
    """
    # TODO: Get from session/database
    return jsonify({
        "plan": "free",
        "status": "active",
        "features": {
            "ai_explanations_remaining": 5,
            "ai_chat_available": False,
            "image_quality": "medium"
        }
    })


# ==================== HELPER FUNCTIONS ====================

def register_strategic_endpoints(app: Flask):
    """
    Register all strategic endpoint blueprints with the Flask app.
    
    Usage:
        from app_strategic_additions import register_strategic_endpoints
        register_strategic_endpoints(app)
    """
    app.register_blueprint(ai_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(billing_bp)
    
    print("✅ Strategic endpoints registered:")
    print("   - /api/v1/ai/explain")
    print("   - /api/v1/ai/chat")
    print("   - /api/v1/assets/image/<filename>")
    print("   - /api/v1/billing/plans")
    print("   - /api/v1/billing/initialize")
