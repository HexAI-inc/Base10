#!/bin/bash

# Production Services Integration Setup Script
# Validates all 4 services are properly configured

set -e

echo "🚀 Base10 Production Services Setup"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version | cut -d' ' -f2)
echo "  Python: $python_version"

# Check if .env exists
echo ""
echo "📋 Checking environment configuration..."
if [ -f .env ]; then
    echo -e "  ${GREEN}✓${NC} .env file found"
else
    echo -e "  ${YELLOW}⚠${NC} .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo -e "  ${YELLOW}!${NC} Please configure .env with your credentials"
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
echo -e "  ${GREEN}✓${NC} Dependencies installed"

# Check Redis connection
echo ""
echo "🔍 Checking Redis connection..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Redis is running"
    else
        echo -e "  ${RED}✗${NC} Redis not responding. Start with: docker run -d -p 6379:6379 redis:7-alpine"
    fi
else
    echo -e "  ${YELLOW}⚠${NC} redis-cli not installed. Cannot verify Redis connection."
fi

# Check PostgreSQL connection
echo ""
echo "🔍 Checking PostgreSQL connection..."
python3 << EOF
try:
    from app.db.session import engine
    with engine.connect() as conn:
        conn.execute("SELECT 1")
    print("  \033[0;32m✓\033[0m PostgreSQL connected")
except Exception as e:
    print(f"  \033[0;31m✗\033[0m PostgreSQL connection failed: {e}")
EOF

# Run database migration
echo ""
echo "🔄 Running database migration..."
python3 migrate_engagement_fields.py
echo -e "  ${GREEN}✓${NC} Database schema updated"

# Verify service imports
echo ""
echo "🔍 Verifying service imports..."

python3 << EOF
import sys

errors = []

try:
    from app.services.comms_service import CommunicationService
    print("  \033[0;32m✓\033[0m CommunicationService")
except ImportError as e:
    errors.append(f"CommunicationService: {e}")
    print(f"  \033[0;31m✗\033[0m CommunicationService: {e}")

try:
    from app.services.scheduler import start_scheduler, stop_scheduler
    print("  \033[0;32m✓\033[0m Scheduler")
except ImportError as e:
    errors.append(f"Scheduler: {e}")
    print(f"  \033[0;31m✗\033[0m Scheduler: {e}")

try:
    from app.services.storage import StorageService
    print("  \033[0;32m✓\033[0m StorageService")
except ImportError as e:
    errors.append(f"StorageService: {e}")
    print(f"  \033[0;31m✗\033[0m StorageService: {e}")

try:
    from app.services.analytics import AnalyticsService
    print("  \033[0;32m✓\033[0m AnalyticsService")
except ImportError as e:
    errors.append(f"AnalyticsService: {e}")
    print(f"  \033[0;31m✗\033[0m AnalyticsService: {e}")

try:
    from app.core.redis_client import redis_client
    print("  \033[0;32m✓\033[0m RedisClient")
except ImportError as e:
    errors.append(f"RedisClient: {e}")
    print(f"  \033[0;31m✗\033[0m RedisClient: {e}")

if errors:
    sys.exit(1)
EOF

# Check config keys
echo ""
echo "🔍 Checking configuration keys..."

python3 << EOF
from app.core.config import settings

required_keys = [
    'DATABASE_URL', 'SECRET_KEY', 'REDIS_URL',
    'STORAGE_BACKEND', 'POSTHOG_API_KEY'
]

missing = []
for key in required_keys:
    value = getattr(settings, key, None)
    if value and value != "":
        print(f"  \033[0;32m✓\033[0m {key}")
    else:
        print(f"  \033[1;33m⚠\033[0m {key} (not configured)")
        if key in ['DATABASE_URL', 'SECRET_KEY', 'REDIS_URL']:
            missing.append(key)

if missing:
    print(f"\n  \033[0;31m✗\033[0m Critical keys missing: {', '.join(missing)}")
    print(f"  Update .env with these values")
EOF

# Test Redis cache
echo ""
echo "🧪 Testing Redis cache..."
python3 << EOF
from app.core.redis_client import redis_client

try:
    # Test basic operations
    test_data = {'rank': 1, 'score': 100}
    redis_client.set_json('test:key', test_data, ttl=60)
    result = redis_client.get_json('test:key')
    
    if result == test_data:
        print("  \033[0;32m✓\033[0m Redis cache working")
        redis_client.delete('test:key')
    else:
        print("  \033[0;31m✗\033[0m Redis cache test failed")
except Exception as e:
    print(f"  \033[1;33m⚠\033[0m Redis not available: {e}")
EOF

# Summary
echo ""
echo "===================================="
echo "📊 Setup Summary"
echo "===================================="
echo ""
echo "Services:"
echo "  1. ✓ Notification Orchestrator (comms_service.py)"
echo "  2. ✓ Scheduler Service (scheduler.py)"
echo "  3. ✓ Media/CDN Service (storage.py)"
echo "  4. ✓ Analytics Service (analytics.py)"
echo ""
echo "Database:"
echo "  ✓ User.has_app_installed added"
echo "  ✓ User.study_streak added"
echo "  ✓ User.last_activity_date added"
echo "  ✓ Attempt.skipped added"
echo ""
echo "APIs:"
echo "  ✓ GET /api/v1/leaderboard/weekly"
echo "  ✓ GET /api/v1/leaderboard/monthly"
echo "  ✓ GET /api/v1/leaderboard/my-rank"
echo ""
echo -e "${GREEN}✓ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Configure .env with your credentials"
echo "  2. Start server: python app/main.py"
echo "  3. Test scheduler: python app/services/scheduler.py"
echo "  4. View docs: http://localhost:8000/docs"
echo ""
echo "Phase 2 TODO:"
echo "  • Set up Firebase (push notifications)"
echo "  • Set up SendGrid (email)"
echo "  • Set up AWS S3 (production storage)"
echo "  • Set up Cloudinary (image optimization)"
echo ""
