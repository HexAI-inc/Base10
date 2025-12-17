# Quick Test Guide - AI Enhancements

## Prerequisites
```bash
# Ensure GOOGLE_API_KEY is set
export GOOGLE_API_KEY="your_gemini_api_key"

# Start server
uvicorn app.main:app --reload
```

## Test 1: Socratic Mode Chat

### Request (Socratic Mode OFF - Direct Answer)
```bash
curl -X POST http://localhost:8000/api/v1/ai/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the quadratic formula?",
    "socratic_mode": false,
    "subject": "MATHEMATICS",
    "history": []
  }'
```

**Expected Response**:
```json
{
  "response": "The quadratic formula is: $$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$ This formula is used to solve quadratic equations of the form $ax^2 + bx + c = 0$...",
  "suggestions": [
    "Show me a worked example",
    "Tell me more about this",
    "Give me a practice question on Quadratic Equations"
  ],
  "related_topics": []
}
```

### Request (Socratic Mode ON - Guided Learning)
```bash
curl -X POST http://localhost:8000/api/v1/ai/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the quadratic formula?",
    "socratic_mode": true,
    "subject": "MATHEMATICS",
    "history": []
  }'
```

**Expected Response**:
```json
{
  "response": "Great question! Before I tell you the formula, let me guide you to understand it. What do you already know about quadratic equations? Can you tell me what form they take?",
  "suggestions": [
    "Can you explain that in your own words?",
    "What makes you think that?",
    "How does this connect to what you learned before?"
  ],
  "related_topics": []
}
```

**Key Difference**: Socratic mode asks guiding questions instead of giving direct answers.

---

## Test 2: AI Quiz Generation

### Request (Easy Math Quiz)
```bash
curl -X POST "http://localhost:8000/api/v1/ai/generate-quiz?subject=MATHEMATICS&topic=Basic Algebra&difficulty=easy&num_questions=3" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response**:
```json
{
  "title": "Basic Algebra Quiz",
  "subject": "MATHEMATICS",
  "topic": "Basic Algebra",
  "difficulty": "easy",
  "num_questions": 3,
  "questions": [
    {
      "question": "Solve for $x$: $2x + 5 = 13$",
      "options": {
        "A": "$x = 4$",
        "B": "$x = 8$",
        "C": "$x = 9$",
        "D": "$x = 6.5$"
      },
      "correct_answer": "A",
      "explanation": "Subtract 5 from both sides: $2x = 8$, then divide by 2: $x = 4$"
    },
    {
      "question": "What is $3x - 2$ when $x = 5$?",
      "options": {
        "A": "$13$",
        "B": "$17$",
        "C": "$15$",
        "D": "$11$"
      },
      "correct_answer": "A",
      "explanation": "Substitute $x = 5$: $3(5) - 2 = 15 - 2 = 13$"
    }
  ]
}
```

### Request (Hard Chemistry Quiz)
```bash
curl -X POST "http://localhost:8000/api/v1/ai/generate-quiz?subject=CHEMISTRY&topic=Chemical Bonding&difficulty=hard&num_questions=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected**: 5 challenging chemistry questions about chemical bonding with detailed explanations.

### Request (General Subject Quiz - No Topic)
```bash
curl -X POST "http://localhost:8000/api/v1/ai/generate-quiz?subject=PHYSICS&difficulty=medium&num_questions=4" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected**: 4 diverse physics questions covering various topics.

---

## Test 3: Quiz Mode Detection

### Request (Ask for Quiz in Chat)
```bash
curl -X POST http://localhost:8000/api/v1/ai/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can you give me a quiz on Quadratic Equations?",
    "subject": "MATHEMATICS",
    "topic": "Quadratic Equations",
    "history": []
  }'
```

**Expected Response**:
```json
{
  "response": "Starting MATHEMATICS Quiz on Quadratic Equations...",
  "suggestions": ["Give me a practice question on Quadratic Equations"],
  "related_topics": []
}
```

**Note**: Response will be cleaned to remove `[QUIZ_MODE: MATHEMATICS | Quadratic Equations]` trigger. Frontend should detect this pattern and call `/ai/generate-quiz`.

---

## Test 4: LaTeX Utilities

### Python Console Test
```python
# Start Python REPL
python3

# Import functions
from app.services.ai_service import clean_for_speech, sanitize_json_output

# Test 1: Clean for speech
text1 = "The quadratic formula is $x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$"
print(clean_for_speech(text1))
# Expected: "The quadratic formula is x = -b plus or minus square root of b to the power of 2 - 4ac over 2a"

# Test 2: Simple power
text2 = "The area is $\\pi r^2$"
print(clean_for_speech(text2))
# Expected: "The area is π r to the power of 2"

# Test 3: Sanitize JSON
latex = "Use \\frac{numerator}{denominator} for fractions"
print(sanitize_json_output(latex))
# Expected: "Use \\\\frac{numerator}{denominator} for fractions"

# Test 4: Multiple backslashes
latex2 = "Formula: \\text{speed} = \\frac{distance}{time}"
print(sanitize_json_output(latex2))
# Expected: "Formula: \\\\text{speed} = \\\\frac{distance}{time}"
```

---

## Test 5: Check AI Status

### Request
```bash
curl -X GET http://localhost:8000/api/v1/ai/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response**:
```json
{
  "available": true,
  "quota_remaining": 100,
  "features": {
    "explain": true,
    "chat": true,
    "quiz_generation": true,
    "socratic_mode": true,
    "premium": false
  },
  "message": "AI services ready"
}
```

**If Gemini not configured**:
```json
{
  "available": false,
  "quota_remaining": 100,
  "features": {
    "explain": true,
    "chat": false,
    "quiz_generation": false,
    "socratic_mode": false,
    "premium": false
  },
  "message": "AI services not configured"
}
```

---

## Test 6: Conversation with History

### Request
```bash
curl -X POST http://localhost:8000/api/v1/ai/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can you explain more about isotopes?",
    "subject": "CHEMISTRY",
    "history": [
      {"role": "user", "content": "What are atoms?"},
      {"role": "assistant", "content": "Atoms are the basic building blocks of matter. They consist of a nucleus containing protons and neutrons, surrounded by electrons."},
      {"role": "user", "content": "What makes elements different?"}
    ]
  }'
```

**Expected**: AI provides contextual response building on previous conversation about atoms.

---

## Test 7: Socratic Mode with Follow-up

### Step 1: Initial Question
```bash
curl -X POST http://localhost:8000/api/v1/ai/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I dont understand fractions",
    "socratic_mode": true,
    "subject": "MATHEMATICS",
    "history": []
  }'
```

**Expected Response**: AI asks what student knows about division or sharing.

### Step 2: Follow-up
```bash
curl -X POST http://localhost:8000/api/v1/ai/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I know division is sharing equally",
    "socratic_mode": true,
    "subject": "MATHEMATICS",
    "history": [
      {"role": "user", "content": "I dont understand fractions"},
      {"role": "assistant", "content": "Lets start with what you know. Can you tell me about sharing things equally? Like if you have 8 cookies and 4 friends?"}
    ]
  }'
```

**Expected Response**: AI builds on student's answer, guiding toward fraction concept.

---

## Test 8: Error Handling

### Test Invalid Quiz Parameters
```bash
# Too many questions
curl -X POST "http://localhost:8000/api/v1/ai/generate-quiz?subject=MATH&num_questions=50" \
  -H "Authorization: Bearer YOUR_TOKEN"
```
**Expected**: Quiz limited to 10 questions (max)

### Test Missing Subject
```bash
curl -X POST "http://localhost:8000/api/v1/ai/generate-quiz?num_questions=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```
**Expected**: 422 Validation Error (subject required)

### Test Invalid Difficulty
```bash
curl -X POST "http://localhost:8000/api/v1/ai/generate-quiz?subject=PHYSICS&difficulty=extreme" \
  -H "Authorization: Bearer YOUR_TOKEN"
```
**Expected**: Defaults to "medium" difficulty

---

## Verification Checklist

### Feature Completeness
- [ ] Socratic mode provides guiding questions (not direct answers)
- [ ] Direct mode provides clear explanations
- [ ] Quiz generation works for all subjects
- [ ] LaTeX formulas are properly formatted (`$formula$` syntax)
- [ ] Suggestions are contextual and relevant
- [ ] Quiz mode detection removes trigger from response
- [ ] Status endpoint reports all new features

### Response Quality
- [ ] Socratic questions are thoughtful and guide learning
- [ ] Direct answers are comprehensive and clear
- [ ] Quiz questions are WAEC-relevant
- [ ] Explanations are detailed with steps
- [ ] LaTeX is properly escaped in JSON

### Performance
- [ ] Chat response time < 3 seconds
- [ ] Quiz generation (5 questions) < 5 seconds
- [ ] No errors in console/logs
- [ ] Proper error handling on failures

### Edge Cases
- [ ] Empty history handled correctly
- [ ] Very long messages handled (truncated if needed)
- [ ] Missing optional fields use defaults
- [ ] Invalid difficulty defaults to medium
- [ ] num_questions clamped to 1-10 range

---

## Common Issues & Solutions

### Issue: "AI service not available"
**Solution**: 
```bash
# Check environment variable
echo $GOOGLE_API_KEY

# Set if missing
export GOOGLE_API_KEY="your_api_key_here"

# Restart server
uvicorn app.main:app --reload
```

### Issue: LaTeX not rendering in response
**Check**: Response should contain `$formula$` or `$$formula$$` syntax
**Frontend**: Ensure using KaTeX or MathJax library

### Issue: Socratic mode gives direct answers
**Check**: Verify request has `"socratic_mode": true`
**Debug**: Add logging to verify SOCRATIC_PROMPT is used

### Issue: Quiz generation times out
**Solution**: Reduce `num_questions` or check Gemini API quota

---

## Performance Benchmarks

Expected response times:
- **Chat (direct mode)**: 1-2 seconds
- **Chat (socratic mode)**: 1-3 seconds
- **Quiz (3 questions)**: 2-4 seconds
- **Quiz (5 questions)**: 3-5 seconds
- **Quiz (10 questions)**: 5-8 seconds
- **Explanation**: 1-2 seconds

If significantly slower, check:
- Network latency to Gemini API
- Server resources (CPU/memory)
- Gemini API quota/rate limits

---

## Next Steps After Testing

1. **Frontend Integration**:
   - Add Socratic mode toggle in chat UI
   - Add "Generate Quiz" button
   - Implement LaTeX rendering (KaTeX)
   - Add quiz mode detection in chat responses

2. **User Feedback**:
   - Collect ratings on AI responses
   - Track which features are most used
   - Monitor quiz completion rates

3. **Analytics**:
   - Track socratic vs direct mode usage
   - Monitor quiz generation by subject
   - Measure learning outcomes

4. **Optimizations**:
   - Cache common quiz topics
   - Implement request throttling
   - Add background quiz generation
   - Pre-generate popular quizzes

---

## Getting User Tokens for Testing

### Method 1: Login via API
```bash
# Register new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User"
  }'

# Login to get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'

# Response will contain:
# {"access_token": "eyJ...", "token_type": "bearer"}
```

### Method 2: Use existing user
```bash
# Login with existing credentials
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "esjallow03@gmail.com",
    "password": "your_password"
  }'
```

Then use token in subsequent requests:
```bash
export TOKEN="eyJ..."

curl -X POST http://localhost:8000/api/v1/ai/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "socratic_mode": true}'
```

---

## Documentation Links

- Full Feature Documentation: `AI_ENHANCEMENTS.md`
- API Reference: http://localhost:8000/docs (Swagger UI)
- Frontend Integration: See AI_ENHANCEMENTS.md "Frontend Integration Guide"
