"""
Data migration script: Import WAEC questions from JSON to PostgreSQL.

Usage:
    python migrate_questions.py
"""
import json
import sys
from pathlib import Path
from sqlalchemy.orm import Session

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.question import Question, Subject, DifficultyLevel


def load_json_questions(json_path: str):
    """Load questions from JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def map_subject(old_subject: str) -> Subject:
    """Map old subject names to new enum values."""
    mapping = {
        'Mathematics': Subject.MATHEMATICS,
        'English Language': Subject.ENGLISH,
        'Physics': Subject.PHYSICS,
        'Chemistry': Subject.CHEMISTRY,
        'Biology': Subject.BIOLOGY,
        'Economics': Subject.ECONOMICS,
        'Geography': Subject.GEOGRAPHY,
        'Literature': Subject.LITERATURE,
        'Government': Subject.GOVERNMENT,
        'History': Subject.HISTORY,
        'Civic Education': Subject.CIVIC_EDUCATION,
        'Commerce': Subject.COMMERCE,
        'Agricultural Science': Subject.AGRICULTURAL_SCIENCE,
        'Computer Science': Subject.COMPUTER_SCIENCE,
        'French': Subject.FRENCH
    }
    return mapping.get(old_subject, Subject.MATHEMATICS)


def map_difficulty(year: int) -> DifficultyLevel:
    """
    Estimate difficulty based on year and other factors.
    For now, using a simple heuristic - can be improved later.
    """
    # Newer questions tend to be slightly harder
    if year >= 2020:
        return DifficultyLevel.HARD
    elif year >= 2015:
        return DifficultyLevel.MEDIUM
    else:
        return DifficultyLevel.EASY


def migrate_questions(db: Session, questions_data: list):
    """
    Migrate questions from JSON structure to database.
    
    Expected JSON structure:
    {
        "id": 1,
        "question": "What is 2+2?",
        "options": ["2", "3", "4", "5"],
        "answer": "C",
        "subject": "Mathematics",
        "topic": "Basic Arithmetic",
        "year": 2020
    }
    """
    migrated = 0
    failed = 0
    
    for q_data in questions_data:
        try:
            # Extract options (A, B, C, D)
            options = q_data.get('options', [])
            if len(options) != 4:
                print(f"⚠️  Question {q_data.get('id')} has {len(options)} options, expected 4. Skipping.")
                failed += 1
                continue
            
            # Calculate correct index from answer (A=0, B=1, C=2, D=3)
            answer_letter = q_data.get('answer', 'A').upper()
            correct_index = ord(answer_letter) - ord('A')
            
            if not (0 <= correct_index <= 3):
                print(f"⚠️  Question {q_data.get('id')} has invalid answer: {answer_letter}. Skipping.")
                failed += 1
                continue
            
            # Create Question model
            question = Question(
                content=q_data.get('question', ''),
                options_json=json.dumps(options),
                correct_index=correct_index,
                explanation=q_data.get('explanation'),
                subject=map_subject(q_data.get('subject', 'Mathematics')),
                topic=q_data.get('topic', 'General'),
                difficulty=map_difficulty(q_data.get('year', 2020)),
                year=q_data.get('year'),
                source='WAEC'
            )
            
            db.add(question)
            migrated += 1
            
            # Commit in batches of 100 for performance
            if migrated % 100 == 0:
                db.commit()
                print(f"✅ Migrated {migrated} questions...")
        
        except Exception as e:
            print(f"❌ Failed to migrate question {q_data.get('id')}: {e}")
            failed += 1
    
    # Final commit
    db.commit()
    
    return migrated, failed


def main():
    """Main migration function."""
    print("🚀 Starting WAEC questions migration...")
    
    # Create tables if they don't exist
    print("📦 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Determine JSON path (try both locations)
    json_paths = [
        Path(__file__).parent / 'data' / 'waec_questions.json',
        Path(__file__).parent / 'WaecQuestions.json'
    ]
    
    json_path = None
    for path in json_paths:
        if path.exists():
            json_path = path
            break
    
    if not json_path:
        print(f"❌ Could not find questions JSON file in: {json_paths}")
        return
    
    print(f"📄 Loading questions from: {json_path}")
    
    # Load JSON data
    try:
        questions_data = load_json_questions(str(json_path))
        print(f"✅ Loaded {len(questions_data)} questions from JSON")
    except Exception as e:
        print(f"❌ Failed to load JSON: {e}")
        return
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Migrate questions
        migrated, failed = migrate_questions(db, questions_data)
        
        print("\n" + "="*50)
        print(f"✅ Migration complete!")
        print(f"   Migrated: {migrated} questions")
        print(f"   Failed: {failed} questions")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
