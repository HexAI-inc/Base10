# Loading WAEC Questions to Database

## Overview
Added support for 3 new subjects and 402 WAEC examination questions covering 7 subjects.

## New Subjects Added
1. **Government** - 52 questions
2. **Civic Education** - questions available
3. **Financial Accounting** - 150 questions

## Existing Subjects with New Questions
- **Geography** - 50 questions
- **Mathematics** - 38 questions  
- **Physics** - 51 questions
- **Biology** - 61 questions

## Files Added
- `app/db/WaecQuestions.json` - 402 questions across 7 subjects
- `load_waec_questions.py` - Python script to bulk load questions
- Migration: `alembic/versions/a66d39049213_add_new_subject_enums.py`

## Database Schema Changes
Updated `Subject` enum in `app/models/question.py`:
```python
class Subject(str, enum.Enum):
    MATHEMATICS = "Mathematics"
    ENGLISH = "English Language"
    PHYSICS = "Physics"
    CHEMISTRY = "Chemistry"
    BIOLOGY = "Biology"
    ECONOMICS = "Economics"
    GEOGRAPHY = "Geography"
    GOVERNMENT = "Government"  # NEW
    CIVIC_EDUCATION = "Civic Education"  # NEW
    FINANCIAL_ACCOUNTING = "Financial Accounting"  # NEW
```

## Deployment Steps

### 1. After Deployment, Run Migration
The migration will add the new enum values to PostgreSQL:

```bash
# SSH into DigitalOcean app container or use App Console
python -m alembic upgrade head
```

### 2. Load Questions into Database
Run the loader script:

```bash
python load_waec_questions.py
```

Expected output:
```
🚀 Loading WAEC questions from JSON...
Found 2 separate JSON arrays
  Parsed array 1: 50 questions
  Parsed array 2: 352 questions
Total questions loaded: 402
  Processed 100/402 questions (100 added, 0 skipped)...
  Processed 200/402 questions (200 added, 0 skipped)...
  Processed 300/402 questions (300 added, 0 skipped)...
  Processed 400/402 questions (400 added, 0 skipped)...

============================================================
✅ Successfully loaded 402 questions!
⏭️  Skipped 0 duplicate questions

Questions by subject:
  • Biology: 61
  • Civic Education: X
  • Financial Accounting: 150
  • Geography: 50
  • Government: 52
  • Mathematics: 38
  • Physics: 51
============================================================
```

## Question Format
Each question includes:
- `subject`: One of the 10 subjects
- `topic`: Specific topic within subject (e.g., "Map Reading", "Algebra")
- `content`: The question text
- `options_json`: JSON array of 4 options
- `correct_index`: Index (0-3) of correct answer
- `difficulty`: EASY, MEDIUM, or HARD
- `explanation`: Detailed explanation of answer
- `exam_year`: e.g., "WASSCE 2015"

## Features
- **Duplicate Detection**: Script checks for existing questions by content and subject
- **Batch Processing**: Commits questions individually for reliability
- **Error Handling**: Continues loading even if some questions fail
- **Multi-Array Support**: Handles JSON files with multiple arrays

## Local Testing (Already Done)
Locally loaded 200 questions successfully:
- Geography: 50
- Mathematics: 38
- Physics: 51
- Biology: 61

The remaining 202 questions (Government, Civic Education, Financial Accounting) require the production PostgreSQL enum migration.

## Verification
After loading, verify via API:

```bash
# Get questions by subject
curl https://your-app.ondigitalocean.app/api/v1/questions/sync?subject=Government&limit=10

# Check total question count
curl https://your-app.ondigitalocean.app/api/v1/questions/sync?limit=1000 | jq 'length'
```

## Notes
- Questions are sourced from WASSCE (West African Senior School Certificate Examination)
- All questions include detailed explanations for learning
- Topics span multiple years (2011-2015+)
- Script is idempotent - can be run multiple times safely
