#!/usr/bin/env python3
"""
Quick test script to verify Resend email integration
"""
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_resend_import():
    """Test that resend package is installed"""
    try:
        import resend
        print("✅ Resend package installed successfully")
        return True
    except ImportError as e:
        print(f"❌ Resend package not found: {e}")
        print("   Run: pip install resend")
        return False

def test_config():
    """Test that environment variables are set"""
    from app.core.config import settings
    
    print("\n📋 Configuration Check:")
    
    if not settings.RESEND_API_KEY:
        print("❌ RESEND_API_KEY not set in .env")
        return False
    elif settings.RESEND_API_KEY.startswith("re_"):
        print(f"✅ RESEND_API_KEY: {settings.RESEND_API_KEY[:10]}...")
    else:
        print("⚠️  RESEND_API_KEY doesn't look valid (should start with 're_')")
        return False
    
    if settings.RESEND_FROM_EMAIL:
        print(f"✅ RESEND_FROM_EMAIL: {settings.RESEND_FROM_EMAIL}")
    else:
        print("❌ RESEND_FROM_EMAIL not set")
        return False
    
    if settings.FRONTEND_URL:
        print(f"✅ FRONTEND_URL: {settings.FRONTEND_URL}")
    else:
        print("⚠️  FRONTEND_URL not set (optional but recommended)")
    
    return True

def test_send_email():
    """Test sending a real email"""
    import resend
    from app.core.config import settings
    
    print("\n📧 Testing Email Send:")
    print("   This will send a real test email...")
    
    # Get recipient email
    recipient = input("\n   Enter your email address to receive test email: ").strip()
    
    if not recipient or '@' not in recipient:
        print("❌ Invalid email address")
        return False
    
    try:
        resend.api_key = settings.RESEND_API_KEY
        
        params = {
            "from": settings.RESEND_FROM_EMAIL,
            "to": [recipient],
            "subject": "🎉 Base10 Email Test - Success!",
            "html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
        <h1 style="color: white; margin: 0;">Base10</h1>
        <p style="color: #f0f0f0; margin: 10px 0 0 0;">Email Service Test</p>
    </div>
    
    <div style="background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; border-top: none;">
        <h2 style="color: #667eea;">✅ Email Integration Successful!</h2>
        <p>Congratulations! Your Resend email service is working perfectly.</p>
        
        <div style="background: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 20px 0;">
            <p style="margin: 0; color: #155724;">
                <strong>✓ Configuration Verified:</strong><br>
                • API Key: Valid<br>
                • From Address: """ + settings.RESEND_FROM_EMAIL + """<br>
                • Domain: cjalloh.com<br>
                • Service: Active
            </p>
        </div>
        
        <h3 style="color: #667eea;">What's Next?</h3>
        <ol style="padding-left: 20px;">
            <li>Start the FastAPI server: <code>uvicorn app.main:app --reload</code></li>
            <li>Test user registration with email verification</li>
            <li>Check onboarding emails for students, teachers, and parents</li>
        </ol>
        
        <p style="margin-top: 30px; font-size: 14px; color: #666;">
            This is an automated test email from Base10 backend.<br>
            If you received this, your email service is ready for production! 🚀
        </p>
    </div>
    
    <div style="background: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; font-size: 12px; color: #999;">
        <p style="margin: 5px 0;">© 2025 Base10. All rights reserved.</p>
    </div>
</body>
</html>
            """
        }
        
        response = resend.Emails.send(params)
        
        print(f"\n✅ Email sent successfully!")
        print(f"   Email ID: {response.get('id', 'unknown')}")
        print(f"   To: {recipient}")
        print(f"   From: {settings.RESEND_FROM_EMAIL}")
        print(f"\n   Check your inbox (and spam folder)!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Email send failed: {e}")
        print(f"\n   Common issues:")
        print(f"   • Domain not verified in Resend dashboard")
        print(f"   • Invalid API key")
        print(f"   • Incorrect from email format")
        print(f"\n   Check: https://resend.com/domains")
        return False

def main():
    print("=" * 60)
    print("🚀 Base10 Email Service Test")
    print("=" * 60)
    
    # Step 1: Check resend package
    if not test_resend_import():
        return 1
    
    # Step 2: Check configuration
    if not test_config():
        return 1
    
    # Step 3: Test sending
    print("\n" + "=" * 60)
    send_test = input("\nDo you want to send a test email? (y/n): ").strip().lower()
    
    if send_test == 'y':
        if test_send_email():
            print("\n" + "=" * 60)
            print("🎉 All tests passed! Email service is ready.")
            print("=" * 60)
            return 0
        else:
            return 1
    else:
        print("\n✓ Configuration looks good. Skipping email send test.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
