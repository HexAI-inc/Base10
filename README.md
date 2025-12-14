# Base10 Backend API

**Offline-first education platform for rural African students**

Built with FastAPI, PostgreSQL, and Docker. Designed for students with $40 phones and spotty 3G connectivity.

---

## 🌟 Features

### Phase 1 (Current)
- ✅ **JWT Authentication** with 7-day tokens for offline usage
- ✅ **Phone-first design** - SMS users don't need email
- ✅ **4000+ WAEC questions** across 15 subjects
- ✅ **Offline sync engine** - Download questions, work offline, sync later
- ✅ **Smart algorithm** - Prioritizes weak topics (<50% accuracy)
- ✅ **Streak tracking** - Gamification for daily engagement
- ✅ **RESTful API** with auto-generated docs

### Planned Features
- **Phase 2**: React Native mobile app with local SQLite
- **Phase 3**: SMS bridge via Twilio/Africa's Talking
- **Phase 4**: Local AI with quantized models (<3GB)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Docker (optional)

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <repo-url>
cd base10-backend

# Start all services (PostgreSQL + FastAPI + Redis)
docker-compose up -d

# Migrate WAEC questions to database
docker-compose exec api python migrate_questions.py

# View logs
docker-compose logs -f api

# API will be available at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup PostgreSQL database
createdb base10_db

# 4. Configure environment
cp .env.example .env
# Edit .env with your database credentials

# 5. Migrate questions
python migrate_questions.py

# 6. Run the server
uvicorn app.main:app --reload

# API available at: http://localhost:8000
```

---

## 📚 API Documentation

### Interactive Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
```http
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

#### Questions
```http
GET  /api/v1/questions/              # Paginated with filters
GET  /api/v1/questions/{id}          # Single question
GET  /api/v1/questions/subjects/list # All subjects
GET  /api/v1/questions/topics/{subject}
GET  /api/v1/questions/random/{subject}
```

#### Offline Sync
```http
POST /api/v1/sync/push               # Upload offline attempts
POST /api/v1/sync/pull               # Download questions for weak topics
GET  /api/v1/sync/stats              # User stats & streak
```

---

## 🔐 Authentication Flow

### 1. Register (Phone-only for SMS users)
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+220123456789",
    "password": "secure123"
  }'
```

### 2. Login (Returns 7-day token)
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=%2B220123456789&password=secure123"
```

### 3. Use Token
```bash
curl http://localhost:8000/api/v1/questions/ \
  -H "Authorization: Bearer <your_token>"
```

---

## 💾 Database Schema

### Users
- `phone_number` (nullable) - For SMS users
- `email` (nullable) - For web users
- `is_verified` - SMS/email verification status
- `last_login` - Last activity timestamp

### Questions
- `content` - Question text (supports LaTeX)
- `options_json` - JSON array of 4 options
- `correct_index` (0-3) - Correct answer
- `subject` - MATHEMATICS, PHYSICS, etc.
- `topic` - Specific topic within subject
- `difficulty` - EASY, MEDIUM, HARD
- `year` - WAEC exam year

### Attempts
- `user_id` - Foreign key to users
- `question_id` - Foreign key to questions
- `is_correct` - Boolean result
- `selected_option` (0-3) - User's choice
- `attempted_at` - When question was attempted
- `device_id` - For deduplication
- `synced_at` - When uploaded to server

---

## 🔄 Offline Sync Algorithm

### Pull Strategy (Download Questions)
1. Calculate weak topics (accuracy < 50%)
2. Return 70% questions from weak topics
3. Return 30% random questions for variety
4. Mobile app caches 200-500 questions locally

### Push Strategy (Upload Attempts)
1. Mobile collects attempts in local SQLite
2. On reconnection, bulk upload to `/sync/push`
3. Server deduplicates by `device_id + question_id + timestamp`
4. Server recalculates weak topics for next pull

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Test specific endpoint
pytest tests/test_sync.py -v
```

### Manual Testing
```bash
# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+220123456789", "password": "test123"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=%2B220123456789&password=test123"

# Get questions (copy token from login response)
curl http://localhost:8000/api/v1/questions/?subject=MATHEMATICS&limit=10 \
  -H "Authorization: Bearer <token>"
```

---

## 📱 Mobile App Integration

### Sync Flow Example (React Native)

```javascript
// 1. Download questions on WiFi
const syncPull = async (token, subjects) => {
  const response = await fetch('http://api.base10.edu/api/v1/sync/pull', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ subjects, limit: 200 })
  });
  
  const data = await response.json();
  
  // Store in local SQLite
  await db.questions.bulkInsert(data.questions);
  
  return data;
};

// 2. Work offline (save to local DB)
const submitAnswer = async (questionId, selectedOption, isCorrect) => {
  await db.attempts.insert({
    question_id: questionId,
    selected_option: selectedOption,
    is_correct: isCorrect,
    attempted_at: new Date(),
    device_id: await getDeviceId(),
    synced: false
  });
};

// 3. Sync when back online
const syncPush = async (token) => {
  const unsyncedAttempts = await db.attempts.find({ synced: false });
  
  const response = await fetch('http://api.base10.edu/api/v1/sync/push', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      device_id: await getDeviceId(),
      attempts: unsyncedAttempts
    })
  });
  
  const result = await response.json();
  
  // Mark as synced
  await db.attempts.updateMany(
    { id: { $in: unsyncedAttempts.map(a => a.id) } },
    { synced: true }
  );
  
  return result;
};
```

---

## 🌍 Deployment

### Railway (1-Click Deploy)
```bash
railway login
railway init
railway link
railway up
railway open
```

### Render (Free Tier)
1. Create PostgreSQL database
2. Create Web Service from GitHub
3. Set environment variables
4. Deploy

### AWS/DigitalOcean
```bash
# Build Docker image
docker build -t base10-api .

# Run container
docker run -d -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host/db \
  -e SECRET_KEY=your-secret \
  base10-api
```

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/base10_db

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days

# CORS (comma-separated)
CORS_ORIGINS=http://localhost:3000,https://base10.edu

# SMS (Phase 3)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1234567890

# Redis
REDIS_URL=redis://localhost:6379/0
```

---

## 📊 Monitoring

### Health Checks
```bash
# Simple health check
curl http://localhost:8000/health

# Detailed status
curl http://localhost:8000/
```

### Logs
```bash
# Docker logs
docker-compose logs -f api

# Database logs
docker-compose logs -f db
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- Built for **IndabaX Sierra Leone Hackathon**
- Powered by **4048 WAEC past questions**
- Inspired by students in rural Gambia and Sierra Leone
- "Education for every student, everywhere 🌍"

---

## 📞 Support

- **Issues**: GitHub Issues
- **Email**: support@base10.edu
- **SMS**: +220XXXXXXX (Phase 3)

---

**Built with ❤️ for African students**
