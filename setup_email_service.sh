#!/bin/bash

# Base10 Email Service Setup Script
# Installs Resend and runs necessary migrations

echo "🚀 Setting up Base10 Email Service with Resend..."
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: No virtual environment detected."
    echo "   It's recommended to activate your venv first:"
    echo "   source venv/bin/activate"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install Resend
echo "📦 Installing Resend Python SDK..."
pip install resend==0.8.0
echo "✅ Resend installed"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your Resend API key:"
    echo "   RESEND_API_KEY=re_your_api_key_here"
    echo "   RESEND_FROM_EMAIL=Base10 <noreply@yourdomain.com>"
    echo ""
else
    echo "✓ .env file already exists"
    echo ""
fi

# Run database migrations
echo "🔄 Running database migrations..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Database migrations completed"
    echo ""
else
    echo "❌ Migration failed. Check errors above."
    exit 1
fi

# Test imports
echo "🧪 Testing Python imports..."
python -c "import resend; print('✅ Resend import successful')"

if [ $? -ne 0 ]; then
    echo "❌ Import test failed"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Email Service Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Get your Resend API key:"
echo "   → Sign up at https://resend.com"
echo "   → Get API key from dashboard"
echo ""
echo "2. Update your .env file:"
echo "   RESEND_API_KEY=re_your_actual_key_here"
echo "   RESEND_FROM_EMAIL=\"Base10 <noreply@yourdomain.com>\""
echo "   FRONTEND_URL=http://localhost:3000"
echo ""
echo "3. Verify your domain in Resend dashboard (for production)"
echo ""
echo "4. Test the email service:"
echo "   python -c \"from app.services.onboarding_service import OnboardingService; print('OK')\""
echo ""
echo "5. Start the server and test registration:"
echo "   uvicorn app.main:app --reload"
echo ""
echo "📖 Read EMAIL_ONBOARDING_GUIDE.md for full documentation"
echo ""
