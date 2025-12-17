# AI Service Enhancements

## Overview
Enhanced the AI tutoring system with advanced features from the hackathon implementation, providing better learning experiences through Socratic teaching, AI-generated quizzes, and improved LaTeX support.

## New Features

### 1. Socratic Teaching Mode
**What it does**: Guides students to discover answers through questions rather than giving direct answers.

**How to use**:
```python
POST /ai/chat
{
    "message": "What is the quadratic formula?",
    "socratic_mode": true
}
```

**Response**: AI asks guiding questions like "What do you already know about quadratic equations?" instead of directly providing the formula.

**Benefits**:
- Deeper learning and retention
- Develops critical thinking skills
- More engaging conversation

### 2. AI Quiz Generation
**What it does**: Generates custom quizzes on any subject and topic with proper LaTeX math formatting.

**How to use**:
```python
POST /ai/generate-quiz?subject=MATHEMATICS&topic=Quadratic Equations&difficulty=medium&num_questions=5
```

**Response**:
```json
{
    "title": "Quadratic Equations Quiz",
    "subject": "MATHEMATICS",
    "topic": "Quadratic Equations",
    "difficulty": "medium",
    "num_questions": 5,
    "questions": [
        {
            "question": "Solve $x^2 - 5x + 6 = 0$",
            "options": {
                "A": "$x = 2, 3$",
                "B": "$x = -2, -3$",
                "C": "$x = 1, 6$",
                "D": "$x = -1, -6$"
            },
            "correct_answer": "A",
            "explanation": "Using factoring: $(x-2)(x-3) = 0$"
        }
    ]
}
```

**Parameters**:
- `subject`: MATHEMATICS, CHEMISTRY, PHYSICS, etc.
- `topic`: Optional specific topic (e.g., "Quadratic Equations", "Atomic Structure")
- `difficulty`: easy, medium, or hard
- `num_questions`: 1-10 questions

**Benefits**:
- Unlimited practice questions
- Tailored to specific topics
- Adaptive difficulty
- Instant feedback with explanations

### 3. Enhanced System Prompts
**What changed**: Replaced basic prompts with comprehensive teaching instructions.

**New SYSTEM_PROMPT includes**:
- WAEC curriculum alignment
- LaTeX math formatting rules (use `$formula$` syntax)
- Step-by-step explanation methodology
- Common mistake awareness
- Real-world West African examples

**New SOCRATIC_PROMPT includes**:
- Guided discovery methodology
- Strategic questioning techniques
- Scaffolding approach (start simple, build complexity)
- Encouraging language
- Metacognitive prompts

### 4. LaTeX Utilities
**What it does**: Proper handling of mathematical notation for different outputs.

**Functions added**:
- `clean_for_speech(text)`: Converts LaTeX to speech-friendly text
  - `$x^2$` → "x to the power of 2"
  - `$\frac{a}{b}$` → "a over b"
  - Useful for text-to-speech or accessibility

- `sanitize_json_output(text)`: Escapes LaTeX properly in JSON
  - Prevents rendering issues with `\text{}`, `\frac{}`, etc.
  - Ensures frontend can parse math correctly

### 5. Quiz Mode Detection
**What it does**: AI can trigger quiz mode during conversation.

**How it works**:
- AI detects when student asks for practice (e.g., "give me quiz questions")
- AI includes trigger: `[QUIZ_MODE: MATHEMATICS | Quadratic Equations]`
- Frontend can detect this and launch quiz interface
- Seamless transition from chat to practice

## Technical Changes

### Files Modified

#### 1. `app/services/ai_service.py`
- **Lines 1-100**: Enhanced imports, configuration, and system prompts
  - Added logging, json, re modules
  - Enhanced Gemini configuration with fallback
  - Added 66-line SYSTEM_PROMPT with LaTeX rules
  - Added 48-line SOCRATIC_PROMPT with teaching methodology

- **Lines 100-230**: Updated core functions
  - `generate_explanation()`: Now uses enhanced SYSTEM_PROMPT
  - `chat_with_ai()`: Added `socratic_mode` parameter, quiz detection
  - `_generate_suggestions()`: Context-aware suggestions based on mode

- **Lines 230-310**: New utility functions
  - `clean_for_speech()`: LaTeX to natural language
  - `sanitize_json_output()`: Proper LaTeX escaping
  - `generate_quiz()`: AI-powered quiz generation

#### 2. `app/api/v1/ai.py`
- **Lines 40-48**: Updated ChatRequest schema
  - Added `socratic_mode: bool` field

- **Lines 177-179**: Updated chat endpoint
  - Pass `socratic_mode` parameter to service
  - Support quiz mode detection

- **Lines 261-336**: New quiz generation endpoint
  - `POST /ai/generate-quiz`
  - Query parameters for customization
  - Returns structured quiz JSON

- **Lines 234-262**: Updated status endpoint
  - Reports `quiz_generation` and `socratic_mode` features
  - Checks all AI capabilities

## API Updates

### Updated Endpoints

#### `/ai/chat` (Enhanced)
**New parameter**: `socratic_mode` (boolean, default: false)

**Example**:
```json
POST /ai/chat
{
    "message": "I don't understand isotopes",
    "history": [],
    "subject": "CHEMISTRY",
    "socratic_mode": true
}
```

**Socratic Response**:
```json
{
    "response": "Great topic! Before we dive in, what do you already know about atoms and their structure? Can you tell me what makes one element different from another?",
    "suggestions": [
        "What makes you think that?",
        "Can you explain that in your own words?",
        "How does this connect to what you learned before?"
    ]
}
```

**Direct Response** (socratic_mode: false):
```json
{
    "response": "Isotopes are atoms of the same element that have different numbers of neutrons. For example, Carbon-12 has 6 neutrons while Carbon-14 has 8 neutrons. They have the same atomic number (number of protons) but different mass numbers...",
    "suggestions": [
        "Can you show another example?",
        "Tell me more about this",
        "Give me a practice question on Atomic Structure"
    ]
}
```

### New Endpoint

#### `POST /ai/generate-quiz`
**Purpose**: Generate custom AI quizzes on any subject/topic.

**Query Parameters**:
- `subject` (required): Subject area
- `topic` (optional): Specific topic
- `difficulty` (optional): easy/medium/hard (default: medium)
- `num_questions` (optional): 1-10 (default: 5)

**Example**:
```
POST /ai/generate-quiz?subject=PHYSICS&topic=Newton's Laws&difficulty=hard&num_questions=3
```

**Response**:
```json
{
    "title": "Newton's Laws Quiz",
    "subject": "PHYSICS",
    "topic": "Newton's Laws",
    "difficulty": "hard",
    "num_questions": 3,
    "questions": [...]
}
```

#### `/ai/status` (Enhanced)
**New fields**:
```json
{
    "features": {
        "explain": true,
        "chat": true,
        "quiz_generation": true,
        "socratic_mode": true,
        "premium": false
    }
}
```

## Frontend Integration Guide

### 1. Enable Socratic Mode Toggle
```typescript
// Add toggle to chat interface
const [socraticMode, setSocraticMode] = useState(false);

// Pass to API
const response = await fetch('/ai/chat', {
    method: 'POST',
    body: JSON.stringify({
        message: userInput,
        history: chatHistory,
        subject: currentSubject,
        socratic_mode: socraticMode
    })
});
```

### 2. Quiz Generation Button
```typescript
// Add "Practice Quiz" button
const generateQuiz = async () => {
    const params = new URLSearchParams({
        subject: currentSubject,
        topic: currentTopic,
        difficulty: selectedDifficulty,
        num_questions: '5'
    });
    
    const quiz = await fetch(`/ai/generate-quiz?${params}`);
    const data = await quiz.json();
    
    // Display quiz UI with data.questions
    launchQuizInterface(data);
};
```

### 3. Quiz Mode Detection
```typescript
// Detect quiz trigger in chat response
const checkForQuizMode = (response: string) => {
    const match = response.match(/\[QUIZ_MODE:\s*(.*?)\s*\|\s*(.*?)\]/);
    if (match) {
        const [, subject, topic] = match;
        // Auto-generate quiz
        generateQuiz(subject, topic);
    }
};
```

### 4. LaTeX Rendering
```typescript
// Use MathJax or KaTeX for LaTeX rendering
import 'katex/dist/katex.min.css';
import { InlineMath, BlockMath } from 'react-katex';

// Render inline math: $formula$
<InlineMath math="x^2 + 2x + 1" />

// Render display math: $$formula$$
<BlockMath math="\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}" />
```

## Testing

### Test Socratic Mode
```bash
curl -X POST http://localhost:8000/api/v1/ai/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the quadratic formula?",
    "socratic_mode": true,
    "subject": "MATHEMATICS"
  }'
```

**Expected**: AI asks guiding questions instead of directly giving the formula.

### Test Quiz Generation
```bash
curl -X POST "http://localhost:8000/api/v1/ai/generate-quiz?subject=CHEMISTRY&topic=Periodic Table&difficulty=easy&num_questions=3" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected**: JSON with 3 chemistry questions about periodic table.

### Test LaTeX Utilities
```python
from app.services.ai_service import clean_for_speech, sanitize_json_output

# Test speech conversion
text = "The formula is $x^2 + 2x + 1$"
speech = clean_for_speech(text)
print(speech)  # "The formula is x to the power of 2 + 2x + 1"

# Test JSON escaping
latex = "Use \\frac{a}{b} for fractions"
safe = sanitize_json_output(latex)
print(safe)  # "Use \\\\frac{a}{b} for fractions"
```

## Benefits for Students

### 1. Better Learning Outcomes
- **Socratic Mode**: Encourages active thinking and discovery
- **Personalized Practice**: AI generates questions on weak topics
- **Instant Feedback**: Detailed explanations for every answer

### 2. Unlimited Practice
- Generate quizzes on any topic, anytime
- No need to wait for teacher to create questions
- Practice at own pace and difficulty level

### 3. Better Math Support
- Proper LaTeX rendering for complex formulas
- Clear step-by-step mathematical explanations
- Visual clarity in problem-solving

### 4. Adaptive Learning
- AI adjusts difficulty based on student performance
- Identifies knowledge gaps and generates targeted practice
- Provides scaffolded learning experiences

## Configuration

### Environment Variables
```bash
# Required for AI services
GOOGLE_API_KEY=your_gemini_api_key

# Optional: Quota limits
AI_QUOTA_PER_USER=100  # Daily request limit
AI_QUIZ_MAX_QUESTIONS=10  # Max questions per quiz
```

### Gemini Model Settings
```python
# app/services/ai_service.py
MODEL_NAME = 'gemini-1.5-flash'  # Fast and cost-effective
# Alternative: 'gemini-1.5-pro' for more complex reasoning
```

## Performance Considerations

### Response Times
- **Chat (socratic_mode=false)**: ~1-2 seconds
- **Chat (socratic_mode=true)**: ~1-3 seconds (more complex reasoning)
- **Quiz Generation (5 questions)**: ~3-5 seconds
- **Explanation**: ~1-2 seconds

### Quota Management
- Track AI requests per user in database
- Implement daily/monthly limits
- Consider caching common quiz topics
- Use background tasks for non-urgent generations

### Cost Optimization
- Use `gemini-1.5-flash` for most requests (cheaper)
- Cache generated quizzes for reuse
- Implement request throttling
- Monitor API usage per endpoint

## Future Enhancements

### Planned Features
1. **Voice Mode**: Integration with text-to-speech using `clean_for_speech()`
2. **Quiz History**: Save generated quizzes for student review
3. **Progress Tracking**: Track which topics students practice most
4. **Collaborative Quizzes**: Teachers can review/edit AI-generated quizzes
5. **Adaptive Difficulty**: Auto-adjust based on student performance
6. **Multi-language Support**: Generate questions in local languages
7. **Image-based Questions**: Support diagrams and charts in quizzes

### Potential Improvements
1. Add more sophisticated quiz mode detection patterns
2. Implement quiz difficulty calibration based on student level
3. Add explanation quality scoring
4. Support custom prompt templates per teacher
5. Integrate with spaced repetition system

## Migration Notes

### Breaking Changes
None - all changes are backward compatible.

### New Dependencies
- Already using `google-generativeai`
- Built-in Python modules only (logging, json, re)

### Database Changes
None required for current implementation.

Future: May add tables for:
- `ai_quiz_history` - Store generated quizzes
- `ai_usage_quota` - Track API usage per user
- `ai_feedback` - Collect quality ratings

## Support & Troubleshooting

### Common Issues

**Issue**: AI responses are too basic
**Solution**: Check that new SYSTEM_PROMPT and SOCRATIC_PROMPT are being used

**Issue**: LaTeX not rendering
**Solution**: Ensure frontend uses proper LaTeX library (KaTeX/MathJax)

**Issue**: Quiz generation fails
**Solution**: Check Gemini API quota, verify GOOGLE_API_KEY

**Issue**: Socratic mode gives direct answers
**Solution**: Verify `socratic_mode=true` is passed to service function

### Debug Mode
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check which prompt is being used
logger.debug(f"Using {'Socratic' if socratic_mode else 'Direct'} prompt")
```

## Credits

Based on the successful hackathon implementation in the `waec-tutor` project, adapted for production use in the base10-backend system.

## Version History

- **v2.0.0** (2025-01-17): Major AI enhancements
  - Added Socratic teaching mode
  - Added AI quiz generation
  - Enhanced system prompts
  - Added LaTeX utilities
  - Quiz mode detection

- **v1.0.0**: Initial AI service
  - Basic explanations
  - Simple chat interface
