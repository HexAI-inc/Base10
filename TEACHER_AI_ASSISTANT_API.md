# Teacher AI Assistant API Documentation

## Overview
The Teacher AI Assistant is a natural language interface that helps teachers manage their classrooms efficiently. Teachers can communicate in plain English to create quizzes, analyze student performance, identify struggling students, and generate reports.

**Key Features:**
- 🤖 Natural language understanding
- 📝 AI-powered quiz generation
- 📊 Performance analytics with psychometric insights
- 🎯 Struggling student identification
- 📋 Automated report generation
- ✅ Teacher review & approval workflow

---

## Endpoints

### 1. AI Assistant Chat
**POST** `/api/v1/teacher/ai-assistant`

Send natural language commands to the AI assistant.

#### Request Body
```json
{
  "message": "Create a quiz on Quadratic Equations for my SS2 class",
  "classroom_id": 5,
  "context": {
    "additional": "context"
  }
}
```

#### Fields
- `message` (required): Natural language command (3-2000 characters)
- `classroom_id` (optional): Classroom context for the command
- `context` (optional): Additional context as key-value pairs

#### Response
```json
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
  "action_summary": "I'll create a 10-question quiz on Quadratic Equations for SS2 students",
  "requires_approval": true,
  "questions_to_clarify": [],
  "quiz_data": {
    "questions": [
      {
        "id": 123,
        "content": "Solve for x: x² + 5x + 6 = 0",
        "options": ["x = -2 or -3", "x = 2 or 3", "x = -1 or -6", "x = 1 or 6"],
        "correct_index": 0,
        "explanation": "Factor the equation: (x+2)(x+3) = 0",
        "subject": "Mathematics",
        "topic": "Quadratic Equations",
        "difficulty": "medium"
      }
    ],
    "total_found": 10,
    "requested": 10,
    "source": "database"
  }
}
```

---

### 2. Approve and Send Quiz
**POST** `/api/v1/teacher/ai-assistant/approve-quiz`

After reviewing AI-generated quiz, approve and send to students.

#### Request Body
```json
{
  "question_ids": [123, 456, 789],
  "classroom_id": 5,
  "title": "Algebra Quiz - Week 3",
  "description": "Practice on quadratic equations",
  "due_date": "2025-01-15T23:59:59Z",
  "points_per_question": 10
}
```

#### Fields
- `question_ids` (required): Array of selected question IDs (min 1)
- `classroom_id` (required): Target classroom ID
- `title` (required): Quiz title (3-200 characters)
- `description` (optional): Quiz description
- `due_date` (optional): Due date in ISO format
- `points_per_question` (optional): Points per correct answer (1-100, default: 10)

#### Response
```json
{
  "id": 45,
  "classroom_id": 5,
  "title": "Algebra Quiz - Week 3",
  "description": "Practice on quadratic equations",
  "subject_filter": "Mathematics",
  "topic_filter": "Quadratic Equations",
  "question_count": 3,
  "due_date": "2025-01-15T23:59:59Z",
  "created_at": "2025-12-31T10:00:00Z"
}
```

---

## Natural Language Commands

### Quiz Creation
```
"Create a quiz on Algebra for SS1"
"Generate 15 questions about Physics for my class"
"Make a hard difficulty quiz on Trigonometry"
"I need practice questions on Photosynthesis"
```

**AI Will:**
1. Extract subject, topic, grade level, difficulty
2. Query question database
3. Return draft questions for review
4. Wait for teacher approval

### Performance Analysis
```
"How is my Physics class doing?"
"Analyze performance for classroom 5"
"Show me stats for this week"
"What's the overall accuracy in my class?"
```

**AI Will:**
1. Calculate accuracy, attempt counts
2. Analyze psychometric data (guessing, struggling)
3. Provide actionable insights
4. Highlight engagement metrics

### Identify Struggling Students
```
"Which students need help?"
"Who is struggling in my class?"
"Show me students with low accuracy"
"Find students with misconceptions"
```

**AI Will:**
1. Analyze individual student performance
2. Calculate accuracy and misconception rates
3. Identify students below 50% accuracy
4. Provide specific recommendations

### Generate Reports
```
"Give me a summary of this week"
"Create a performance report for my class"
"Show me what happened this month"
"Generate a classroom overview"
```

**AI Will:**
1. Compile performance metrics
2. List struggling students
3. Generate AI-written summary
4. Provide actionable recommendations

---

## Response Intents

### `create_quiz`
Returns quiz questions from database for review.

**Response includes:**
- `quiz_data.questions[]` - Array of question objects
- `requires_approval: true` - Teacher must approve before sending

### `analyze_performance`
Returns classroom performance metrics.

**Response includes:**
- `analysis.accuracy` - Overall class accuracy %
- `analysis.guessing_rate` - % of fast answers (< 2 sec)
- `analysis.struggle_rate` - % of slow answers (> 60 sec)
- `analysis.insights[]` - Actionable recommendations

### `identify_struggling`
Returns list of students needing help.

**Response includes:**
- `struggling_students.students[]` - Array of student objects
- Each student has: accuracy, misconception rate, needs_help_with
- `struggling_students.recommendations[]` - Teaching strategies

### `generate_report`
Returns comprehensive classroom report.

**Response includes:**
- `report.summary` - AI-generated overview
- `report.performance_metrics` - Detailed stats
- `report.struggling_students` - Students needing help

### `general_query`
Handles non-actionable questions.

**Response includes:**
- Conversational response
- Suggestions for actionable commands

---

## Psychometric Insights

The AI analyzes student behavior patterns:

### **Guessing Detection**
- **Trigger:** Answer given in < 2 seconds
- **Indication:** Student may be rushing or guessing
- **Recommendation:** Encourage careful reading

### **Struggle Detection**
- **Trigger:** Answer takes > 60 seconds
- **Indication:** Student finding concept difficult
- **Recommendation:** Provide additional resources

### **Misconception Detection**
- **Trigger:** High confidence (4-5) + Wrong answer
- **Indication:** Student has incorrect understanding
- **Recommendation:** Address specific misconception directly

---

## Workflow Example

### 1. Teacher Asks AI
```javascript
POST /api/v1/teacher/ai-assistant
{
  "message": "Create a quiz on Algebra for SS2 with 5 questions",
  "classroom_id": 10
}
```

### 2. AI Returns Draft
```javascript
{
  "intent": "create_quiz",
  "requires_approval": true,
  "quiz_data": {
    "questions": [/* 5 questions */],
    "total_found": 5
  }
}
```

### 3. Teacher Reviews & Approves
```javascript
POST /api/v1/teacher/ai-assistant/approve-quiz
{
  "question_ids": [1, 2, 3, 4, 5],
  "classroom_id": 10,
  "title": "Algebra Practice Quiz",
  "due_date": "2025-01-10T23:59:59Z",
  "points_per_question": 10
}
```

### 4. Quiz Sent to Students
Assignment created and published to classroom. Students see it in their assignments list.

---

## Error Handling

### AI Not Available
```json
{
  "error": "AI Assistant is currently unavailable",
  "message": "Please try again later or contact support"
}
```

### Invalid Request
```json
{
  "error": "Failed to understand request",
  "message": "Please rephrase your request more clearly"
}
```

### Permission Denied
```json
{
  "detail": "Only teachers can use the AI assistant"
}
```

### Classroom Not Found
```json
{
  "detail": "Classroom not found or you don't have permission"
}
```

---

## Best Practices

### 1. **Be Specific**
✅ "Create a 10-question quiz on Quadratic Equations for SS2"
❌ "Make a quiz"

### 2. **Provide Context**
Always include `classroom_id` when available for more accurate responses.

### 3. **Review Before Approving**
AI-generated quizzes should be reviewed for:
- Question quality
- Appropriate difficulty
- Correct answers
- Clear explanations

### 4. **Use Insights**
Act on AI recommendations:
- Schedule review sessions for struggling topics
- Provide one-on-one help to identified students
- Adjust teaching pace based on struggle rates

### 5. **Regular Reports**
Generate weekly reports to track progress over time.

---

## Integration Examples

### React/Next.js (Web)
```javascript
const sendAICommand = async (message, classroomId) => {
  const response = await fetch('/api/v1/teacher/ai-assistant', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message,
      classroom_id: classroomId
    })
  });
  
  const data = await response.json();
  
  if (data.requires_approval && data.quiz_data) {
    // Show review UI
    showQuizReview(data.quiz_data.questions);
  } else if (data.analysis) {
    // Show performance dashboard
    showAnalytics(data.analysis);
  }
  
  return data;
};

// Approve quiz
const approveQuiz = async (questionIds, classroomId, title) => {
  const response = await fetch('/api/v1/teacher/ai-assistant/approve-quiz', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      question_ids: questionIds,
      classroom_id: classroomId,
      title,
      due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
      points_per_question: 10
    })
  });
  
  return response.json();
};
```

### React Native (Mobile)
```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';

const useTeacherAI = () => {
  const sendCommand = async (message, classroomId) => {
    const token = await AsyncStorage.getItem('token');
    
    const response = await fetch('https://api.base10.app/api/v1/teacher/ai-assistant', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message,
        classroom_id: classroomId
      })
    });
    
    return response.json();
  };
  
  return { sendCommand };
};

// Usage in component
const TeacherAssistant = ({ classroomId }) => {
  const { sendCommand } = useTeacherAI();
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState(null);
  
  const handleSubmit = async () => {
    const result = await sendCommand(message, classroomId);
    setResponse(result);
  };
  
  return (
    <View>
      <TextInput
        placeholder="Ask AI Assistant..."
        value={message}
        onChangeText={setMessage}
      />
      <Button title="Send" onPress={handleSubmit} />
      {response && <ResultView data={response} />}
    </View>
  );
};
```

---

## Security & Permissions

- **Authentication Required:** All endpoints require valid JWT token
- **Teacher Role Only:** Only users with `TEACHER` or `ADMIN` role can access
- **Classroom Ownership:** Teachers can only manage their own classrooms
- **Data Privacy:** Student data is aggregated and anonymized in reports

---

## Rate Limits

- **AI Assistant:** 100 requests per hour per teacher
- **Quiz Approval:** Unlimited
- **Best Practice:** Cache AI responses to avoid redundant calls

---

## Troubleshooting

### "AI service not available"
- Check `GOOGLE_API_KEY` in environment variables
- Verify Gemini API is accessible
- Check server logs for detailed errors

### "Failed to understand request"
- Rephrase command more clearly
- Include more context (subject, topic, classroom)
- Use example commands as templates

### "Questions not found"
- Verify question IDs exist in database
- Check if questions were deleted
- Ensure questions match classroom subject

---

## Future Enhancements

- [ ] Multi-language support (French, Portuguese)
- [ ] Voice commands
- [ ] Auto-grading essay questions
- [ ] Personalized study plans per student
- [ ] Parent communication suggestions
- [ ] Curriculum alignment checking

---

## Support

**Technical Issues:** cjalloh25@gmail.com
**Documentation:** [TEACHER_TESTING_COMPLETE.md](./TEACHER_TESTING_COMPLETE.md)
**Status:** ✅ Production Ready
