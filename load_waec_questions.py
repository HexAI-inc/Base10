#!/usr/bin/env python3
"""
Script to load WAEC questions from WaecQuestions.json into the database.
Handles multiple subjects and proper enum mapping.
"""
import json
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.models.question import Question, Subject, DifficultyLevel


def parse_enum_value(enum_string: str, enum_class):
    """
    Parse enum string like 'Subject.GEOGRAPHY' to actual enum value.
    """
    if '.' in enum_string:
        # Extract the enum member name (e.g., 'GEOGRAPHY' from 'Subject.GEOGRAPHY')
        enum_member = enum_string.split('.')[-1]
        return enum_class[enum_member]
    return enum_class(enum_string)


def load_questions_from_json(json_file_path: str):
    """
    Load questions from JSON file and insert them into the database.
    Handles multiple JSON arrays in one file.
    """
    # Read file content
    with open(json_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file contains multiple JSON arrays by trying to parse
    questions_data = []
    try:
        # Try parsing as single array first
        questions_data = json.loads(content)
        print(f"Found {len(questions_data)} questions to load")
    except json.JSONDecodeError:
        print("Single array parse failed, attempting to parse multiple arrays...")
        
        # Split into separate JSON arrays
        # Look for pattern of ]\n[ or ][ 
        import re
        array_pattern = r'\]\s*\['
        parts = re.split(array_pattern, content)
        
        print(f"Found {len(parts)} separate JSON arrays")
        
        for i, part in enumerate(parts):
            # Add back the array brackets
            if i == 0:
                # First part already has opening [
                part = part + ']'
            elif i == len(parts) - 1:
                # Last part already has closing ]
                part = '[' + part
            else:
                # Middle parts need both
                part = '[' + part + ']'
            
            try:
                chunk_data = json.loads(part)
                questions_data.extend(chunk_data)
                print(f"  Parsed array {i+1}: {len(chunk_data)} questions")
            except json.JSONDecodeError as e:
                print(f"  Error parsing array {i+1}: {e}")
                continue
        
        print(f"Total questions loaded: {len(questions_data)}")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Track statistics
        subjects_count = {}
        added_count = 0
        skipped_count = 0
        
        for idx, q_data in enumerate(questions_data, 1):
            try:
                # Parse enums
                subject = parse_enum_value(q_data['subject'], Subject)
                difficulty = parse_enum_value(q_data['difficulty'], DifficultyLevel)
                
                # Check if question already exists (by content and subject)
                existing = db.query(Question).filter(
                    Question.content == q_data['content'],
                    Question.subject == subject
                ).first()
                
                if existing:
                    skipped_count += 1
                    continue
                
                # Create question
                question = Question(
                    subject=subject,
                    topic=q_data['topic'],
                    content=q_data['content'],
                    options_json=q_data['options_json'],
                    correct_index=q_data['correct_index'],
                    difficulty=difficulty,
                    explanation=q_data.get('explanation'),
                    exam_year=q_data.get('exam_year')
                )
                
                db.add(question)
                
                # Commit individually to avoid transaction rollback cascades
                try:
                    db.commit()
                    added_count += 1
                    
                    # Track subject counts
                    subject_name = subject.value
                    subjects_count[subject_name] = subjects_count.get(subject_name, 0) + 1
                    
                    if added_count % 100 == 0:
                        print(f"  Processed {idx}/{len(questions_data)} questions ({added_count} added, {skipped_count} skipped)...")
                except Exception as commit_error:
                    db.rollback()
                    print(f"  Error committing question {idx}: {commit_error}")
                    print(f"  Question: {q_data.get('content', 'N/A')[:100]}")
                    continue
                
            except Exception as e:
                db.rollback()
                print(f"  Error processing question {idx}: {e}")
                print(f"  Question data: {q_data.get('content', 'N/A')[:100]}")
                continue
        
        # No final commit needed since we commit individually
        
        # Print statistics
        print("\n" + "="*60)
        print(f"✅ Successfully loaded {added_count} questions!")
        print(f"⏭️  Skipped {skipped_count} duplicate questions")
        print("\nQuestions by subject:")
        for subject, count in sorted(subjects_count.items()):
            print(f"  • {subject}: {count}")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error loading questions: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    json_file = "app/db/WaecQuestions.json"
    
    if not Path(json_file).exists():
        print(f"❌ File not found: {json_file}")
        sys.exit(1)
    
    print("🚀 Loading WAEC questions from JSON...")
    load_questions_from_json(json_file)
