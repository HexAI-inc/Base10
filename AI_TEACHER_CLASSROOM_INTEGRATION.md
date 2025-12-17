# AI Teacher & Student Classroom Access

## Overview
The AI Teacher is now fully integrated into the classroom system with context-aware responses. Students can see their enrolled classrooms and ask the AI teacher questions with full subject/topic awareness.

---

## 🎓 Student Classroom Access

### Problem Fixed
**Before:** `GET /classrooms` only showed teacher's classrooms  
**After:** Students can now see all classrooms they're enrolled in

### Endpoint: List My Classrooms
```http
GET /api/v1/classrooms
Authorization: Bearer {token}
```

**Response for Teachers:**
```json
[
  {
    "id": 5,
    "name": "Form 3 Mathematics",
    "description": "Advanced algebra and geometry",
    "subject": "Mathematics",
    "grade_level": "Grade 10",
    "join_code": "MATH-778",
    "student_count": 25,
    "role": "teacher",
    "is_active": true,
    "created_at": "2025-12-01T08:00:00Z"
  }
]
```

**Response for Students:**
```json
[
  {
    "id": 5,
    "name": "Form 3 Mathematics",
    "description": "Advanced algebra and geometry",
    "subject": "Mathematics",
    "grade_level": "Grade 10",
    "teacher_name": "Mr. Jalloh",
    "student_count": 25,
    "role": "student",
    "is_active": true,
    "created_at": "2025-12-01T08:00:00Z"
  },
  {
    "id": 8,
    "name": "Physics Lab",
    "description": "Experimental physics",
    "subject": "Physics",
    "grade_level": "Grade 11",
    "teacher_name": "Dr. Kamara",
    "student_count": 18,
    "role": "student",
    "is_active": true,
    "created_at": "2025-12-05T10:00:00Z"
  }
]
```

**Key Differences:**
- **Teachers see:** `join_code` (to share with students)
- **Students see:** `teacher_name` (who's teaching the class)
- **Both see:** `role` field indicating their relationship to the classroom

---

## 🤖 AI Teacher Integration

### Context-Aware AI Assistant

The AI Teacher now operates **within classroom context**, providing responses tailored to:
- Classroom subject (Math, Physics, Biology, etc.)
- Grade level (JSS1, JSS3, SS1, etc.)
- Recent assignment topics
- Student's learning history

### Endpoint: Ask AI Teacher
```http
POST /api/v1/classrooms/{classroom_id}/ask-ai
Authorization: Bearer {token}
Content-Type: application/json

{
  "question": "Can you explain quadratic equations?",
  "context": "I'm struggling with the factoring method"
}
```

**Response:**
```json
{
  "answer": "Let me explain quadratic equations at your Form 3 level...\n\n[Detailed, pedagogical explanation tailored to the classroom subject and grade level]\n\nFor example, if we have x² + 5x + 6 = 0:\n1. Find factors of 6 that add to 5\n2. Those are 2 and 3\n3. So (x + 2)(x + 3) = 0\n4. Therefore x = -2 or x = -3\n\nWould you like me to walk through another example?",
  "classroom_name": "Form 3 Mathematics",
  "subject": "Mathematics",
  "timestamp": "2025-12-17T14:30:00Z"
}
```

---

## 🧠 AI Teacher Capabilities

### 1. Subject-Specific Expertise
The AI knows the classroom subject and adjusts explanations:

**In Math Classroom:**
```
Question: "What is force?"
AI: "Force is a mathematical concept in physics, but since this is a mathematics class, let me explain how we use vectors to represent forces mathematically..."
```

**In Physics Classroom:**
```
Question: "What is force?"
AI: "Force is a push or pull that can change an object's motion. According to Newton's Second Law, F = ma..."
```

### 2. Grade-Appropriate Responses
AI adjusts complexity based on `grade_level`:

**JSS1 (Grade 7):**
- Simple language
- Basic examples
- Step-by-step breakdowns

**SS3 (Grade 12):**
- Advanced concepts
- Complex examples
- Exam-level rigor

### 3. Contextual Awareness
AI references recent classroom topics:

```json
{
  "question": "Can you give me practice problems?",
  "context": null
}
```

**AI Response:**
```
Based on recent topics in Form 3 Mathematics:
- Last assignment: "Quadratic Equations Practice"
- Before that: "Factoring Polynomials"

Here are 3 practice problems on quadratic equations:
1. Solve: x² + 7x + 12 = 0
2. Solve: 2x² - 8x + 6 = 0
3. Find the roots: x² - 5x - 14 = 0
```

---

## 🎯 Use Cases

### Student Asking for Help
```typescript
// Student struggling with homework
const askQuestion = async (classroomId: number, question: string) => {
  const response = await fetch(
    `${API_BASE}/api/v1/classrooms/${classroomId}/ask-ai`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ question })
    }
  );
  
  return response.json();
};

// Usage
const help = await askQuestion(5, "How do I solve this equation: 3x + 5 = 14?");
console.log(help.answer);
```

### Pre-Test Preparation
```typescript
// Student preparing for quiz
const response = await askQuestion(
  5,
  "Can you quiz me on photosynthesis?",
  "We have a test tomorrow"
);

// AI generates practice questions based on classroom context
```

### Homework Assistance
```typescript
// Student working on assignment
const help = await askQuestion(
  5,
  "I don't understand how to factor x² + 6x + 8",
  "This is from Assignment 3, question 5"
);

// AI provides step-by-step explanation
```

---

## 🔒 Permissions

### Who Can Ask AI Teacher?
- ✅ **Teachers** in the classroom
- ✅ **Students** enrolled in the classroom
- ❌ Users not in the classroom

### Access Control
```python
# Backend checks
is_teacher = classroom.teacher_id == user.id
is_student = user in classroom.students

if not (is_teacher or is_student):
    raise HTTPException(403, "Not a member of this classroom")
```

---

## 📊 AI Teacher Behavior

### Pedagogical Approach
The AI acts as a **teaching assistant**, not just an answer bot:

**What AI Does:**
- ✅ Explains concepts clearly
- ✅ Provides examples
- ✅ Asks follow-up questions
- ✅ Encourages critical thinking
- ✅ Relates to classroom topics
- ✅ Adjusts to student's level

**What AI Doesn't Do:**
- ❌ Just give answers without explanation
- ❌ Do homework for students
- ❌ Provide exam answers
- ❌ Replace human teachers

### Example Interactions

**Student:** "What's the answer to 5 + 5?"  
**AI:** "That's 10! But let me help you understand why. When we add 5 + 5, we're combining two groups of 5 objects. Can you think of a real-world example where you'd add two groups of 5?"

**Student:** "Can you do my homework?"  
**AI:** "I can't do your homework for you, but I can help you understand how to solve the problems! Let's work through the first question together. What part are you stuck on?"

**Student:** "I don't get quadratic equations at all"  
**AI:** "Let's break it down step by step! Quadratic equations are just equations where the highest power of x is 2 (like x²). Think of them as puzzles to solve. What's confusing you most - the x² part, factoring, or something else?"

---

## 🎨 Frontend Integration

### Student Dashboard
```typescript
function StudentClassroomList() {
  const [classrooms, setClassrooms] = useState<Classroom[]>([]);
  
  useEffect(() => {
    fetch(`${API_BASE}/api/v1/classrooms`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(res => res.json())
    .then(data => setClassrooms(data));
  }, []);
  
  return (
    <div className="student-classrooms">
      <h2>My Classrooms</h2>
      
      {classrooms.filter(c => c.role === 'student').map(classroom => (
        <ClassroomCard 
          key={classroom.id}
          classroom={classroom}
          onClick={() => navigate(`/classroom/${classroom.id}`)}
        >
          <div className="classroom-header">
            <h3>{classroom.name}</h3>
            <span className="subject">{classroom.subject}</span>
          </div>
          
          <div className="classroom-info">
            <p>Teacher: {classroom.teacher_name}</p>
            <p>{classroom.student_count} students</p>
          </div>
          
          <div className="classroom-actions">
            <button onClick={() => navigate(`/classroom/${classroom.id}/stream`)}>
              📢 Stream
            </button>
            <button onClick={() => navigate(`/classroom/${classroom.id}/assignments`)}>
              📝 Assignments
            </button>
            <button onClick={() => openAIChat(classroom.id)}>
              🤖 Ask AI
            </button>
          </div>
        </ClassroomCard>
      ))}
    </div>
  );
}
```

### AI Teacher Chat Interface
```typescript
function AITeacherChat({ classroomId }: { classroomId: number }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  
  const askAI = async () => {
    if (!question.trim()) return;
    
    // Add user message
    setMessages(prev => [...prev, {
      role: 'user',
      content: question,
      timestamp: new Date()
    }]);
    
    setLoading(true);
    
    try {
      const response = await fetch(
        `${API_BASE}/api/v1/classrooms/${classroomId}/ask-ai`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ question })
        }
      );
      
      const data = await response.json();
      
      // Add AI response
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer,
        timestamp: new Date()
      }]);
      
      setQuestion("");
    } catch (error) {
      console.error('Failed to get AI response:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="ai-chat">
      <div className="chat-header">
        <h3>🤖 AI Teaching Assistant</h3>
        <p>Ask questions about the classroom topics</p>
      </div>
      
      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div className="message-avatar">
              {msg.role === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-content">
              {msg.content}
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="message assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <span className="typing">AI is thinking...</span>
            </div>
          </div>
        )}
      </div>
      
      <div className="chat-input">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && askAI()}
          placeholder="Ask a question about the class..."
        />
        <button onClick={askAI} disabled={loading || !question.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}
```

---

## 🧪 Testing

### Test Student Classroom Listing
```bash
# Login as student
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "student@test.com", "password": "test123"}'

# Get enrolled classrooms
curl "http://localhost:8000/api/v1/classrooms" \
  -H "Authorization: Bearer {student_token}"

# Should see classrooms where role="student"
```

### Test AI Teacher
```bash
# Ask AI in classroom context
curl -X POST "http://localhost:8000/api/v1/classrooms/5/ask-ai" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Can you explain the Pythagorean theorem?",
    "context": "I need help with right triangles"
  }'

# Should get contextual response based on classroom subject
```

---

## 📈 Benefits

### For Students
- **Easy Access:** See all enrolled classrooms in one place
- **24/7 Help:** AI teacher available anytime
- **Personalized:** Responses tailored to classroom and grade level
- **Safe Learning:** Ask "silly questions" without judgment
- **Homework Support:** Get help without revealing answers

### For Teachers
- **Reduced Burden:** AI handles routine questions
- **Better Engagement:** Students get immediate help
- **Context Preserved:** AI reinforces classroom topics
- **Quality Control:** AI encourages learning, not cheating
- **Scalable Support:** Help all students simultaneously

---

## 🚀 Future Enhancements

### Phase 2: AI Memory
- [ ] AI remembers previous conversations
- [ ] Tracks student's weak areas
- [ ] Adaptive difficulty in explanations

### Phase 3: Proactive AI
- [ ] AI suggests practice when detecting struggles
- [ ] Pre-test preparation recommendations
- [ ] Study plan generation

### Phase 4: AI Grading Assistant
- [ ] Auto-grade essay submissions (draft)
- [ ] Suggest feedback for teachers
- [ ] Identify common misconceptions

### Phase 5: Voice AI
- [ ] Voice questions (audio input)
- [ ] Voice responses (TTS)
- [ ] Conversation mode

---

## 🐛 Error Handling

### AI Service Unavailable
```json
{
  "status": 503,
  "detail": "AI teacher is currently unavailable"
}
```
**Cause:** Gemini API not configured or down  
**Fix:** Set `GEMINI_API_KEY` in environment

### Not Classroom Member
```json
{
  "status": 403,
  "detail": "Not a member of this classroom"
}
```
**Cause:** User trying to access classroom they're not in  
**Fix:** Join classroom first with join code

### Rate Limiting (Future)
```json
{
  "status": 429,
  "detail": "Too many AI requests. Please wait 1 minute."
}
```
**Cause:** Abuse prevention  
**Fix:** Add rate limiting per user/classroom

---

## ✅ Summary

**Students Can Now:**
- ✅ See all classrooms they're enrolled in (`GET /classrooms`)
- ✅ Ask AI teacher questions in classroom context (`POST /classrooms/{id}/ask-ai`)
- ✅ Get subject-specific, grade-appropriate responses
- ✅ Access 24/7 homework help

**AI Teacher Provides:**
- ✅ Context-aware responses (subject, grade, recent topics)
- ✅ Pedagogical explanations (not just answers)
- ✅ Encouragement and guidance
- ✅ Safe learning environment

**System Benefits:**
- ✅ Reduced teacher burden for routine questions
- ✅ Increased student engagement
- ✅ Better learning outcomes
- ✅ Scalable support for all students

---

**Status:** ✅ Fully integrated and ready for testing  
**API Version:** v1  
**Last Updated:** December 17, 2025
