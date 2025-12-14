"""
Script to create sample data for testing teacher analytics.
Creates teachers, students, classrooms, questions, and attempts with varied psychometric patterns.
"""
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.classroom import Classroom, Assignment
from app.models.question import Question, Subject, DifficultyLevel
from app.models.progress import Attempt


def create_sample_data():
    """Create comprehensive sample data for testing."""
    db: Session = SessionLocal()
    
    try:
        print("🎓 Creating sample data for teacher analytics testing...")
        
        # Create teacher
        teacher = User(
            email="demo_teacher@base10.edu",
            phone_number="+1555000001",
            hashed_password="$2b$12$hashedpassword",  # bcrypt hash
            full_name="Demo Teacher"
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        print(f"✅ Created teacher: {teacher.full_name} (ID: {teacher.id})")
        
        # Create classroom
        classroom = Classroom(
            teacher_id=teacher.id,
            name="Grade 10 Mathematics - Demo",
            description="Sample classroom for analytics testing",
            join_code="DEMO-101",
            is_active=True
        )
        db.add(classroom)
        db.commit()
        db.refresh(classroom)
        print(f"✅ Created classroom: {classroom.name} (Join Code: {classroom.join_code})")
        
        # Create questions across different topics
        questions = [
            Question(
                subject=Subject.MATHEMATICS,
                topic="Algebra",
                content="Solve for x: 2x + 5 = 15",
                options_json='["x = 5", "x = 10", "x = 7.5", "x = 20"]',
                correct_option=0,
                difficulty=DifficultyLevel.EASY,
                explanation="2x = 15 - 5 = 10, so x = 5"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Algebra",
                content="Factor: x² - 9",
                options_json='["(x-3)(x+3)", "(x-9)(x+1)", "x(x-9)", "(x-3)²"]',
                correct_option=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Difference of squares: a² - b² = (a-b)(a+b)"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Geometry",
                content="Area of a circle with radius 7",
                options_json='["49π", "14π", "7π", "98π"]',
                correct_option=0,
                difficulty=DifficultyLevel.EASY,
                explanation="A = πr² = π(7)² = 49π"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Geometry",
                content="Pythagorean theorem: a² + b² = ?",
                options_json='["c²", "2c", "c", "ab"]',
                correct_option=0,
                difficulty=DifficultyLevel.EASY,
                explanation="In a right triangle, a² + b² = c²"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Trigonometry",
                content="sin²θ + cos²θ = ?",
                options_json='["1", "0", "2", "θ"]',
                correct_option=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Fundamental trigonometric identity"
            ),
        ]
        
        db.add_all(questions)
        db.commit()
        for q in questions:
            db.refresh(q)
        print(f"✅ Created {len(questions)} questions across topics: Algebra, Geometry, Trigonometry")
        
        # Create students with different performance patterns
        student_patterns = [
            {
                "name": "Alice Strong",
                "email": "alice@student.test",
                "phone": "+1555000010",
                "pattern": "strong",  # High accuracy, good confidence
            },
            {
                "name": "Bob Guesser",
                "email": "bob@student.test",
                "phone": "+1555000011",
                "pattern": "guesser",  # Fast responses, low accuracy
            },
            {
                "name": "Carol Struggles",
                "email": "carol@student.test",
                "phone": "+1555000012",
                "pattern": "struggles",  # Slow responses, needs help
            },
            {
                "name": "David Misconception",
                "email": "david@student.test",
                "phone": "+1555000013",
                "pattern": "misconception",  # High confidence but wrong
            },
            {
                "name": "Eva Average",
                "email": "eva@student.test",
                "phone": "+1555000014",
                "pattern": "average",  # Mixed performance
            },
        ]
        
        students = []
        for sp in student_patterns:
            student = User(
                email=sp["email"],
                phone_number=sp["phone"],
                hashed_password="$2b$12$hashedpassword",
                full_name=sp["name"]
            )
            db.add(student)
            students.append((student, sp["pattern"]))
        
        db.commit()
        for student, _ in students:
            db.refresh(student)
        print(f"✅ Created {len(students)} students with varied learning patterns")
        
        # Add students to classroom
        from app.models.classroom import classroom_students
        for student, _ in students:
            db.execute(
                classroom_students.insert().values(
                    classroom_id=classroom.id,
                    student_id=student.id,
                    joined_at=datetime.utcnow() - timedelta(days=10)
                )
            )
        db.commit()
        print(f"✅ Added all students to classroom")
        
        # Create attempts based on student patterns
        attempts = []
        base_time = datetime.utcnow() - timedelta(days=5)
        
        for student, pattern in students:
            for i, question in enumerate(questions):
                attempt_time = base_time + timedelta(hours=i)
                
                if pattern == "strong":
                    # Alice: High accuracy, appropriate confidence
                    attempts.append(Attempt(
                        user_id=student.id,
                        question_id=question.id,
                        is_correct=True if i < 4 else False,  # 80% accuracy
                        selected_option=question.correct_option if i < 4 else (question.correct_option + 1) % 4,
                        attempted_at=attempt_time,
                        time_taken_ms=15000 + (i * 1000),  # 15-20 seconds
                        confidence_level=4 if i < 4 else 3,
                        network_type="wifi",
                        app_version="1.0.0"
                    ))
                
                elif pattern == "guesser":
                    # Bob: Fast, low confidence, poor accuracy
                    attempts.append(Attempt(
                        user_id=student.id,
                        question_id=question.id,
                        is_correct=i % 3 == 0,  # ~33% accuracy
                        selected_option=(question.correct_option + i) % 4,
                        attempted_at=attempt_time,
                        time_taken_ms=1200 + (i * 100),  # <2s = guessing
                        confidence_level=1 if i % 2 == 0 else 2,
                        network_type="3g",
                        app_version="1.0.0"
                    ))
                
                elif pattern == "struggles":
                    # Carol: Very slow, multiple topics struggling
                    attempts.append(Attempt(
                        user_id=student.id,
                        question_id=question.id,
                        is_correct=i % 4 == 0,  # 25% accuracy
                        selected_option=(question.correct_option + 2) % 4,
                        attempted_at=attempt_time,
                        time_taken_ms=65000 + (i * 5000),  # >60s = struggling
                        confidence_level=2,
                        network_type="2g",
                        app_version="0.9.5"
                    ))
                
                elif pattern == "misconception":
                    # David: High confidence but wrong (common misconceptions)
                    is_correct = i == 0  # Only gets first one right
                    attempts.append(Attempt(
                        user_id=student.id,
                        question_id=question.id,
                        is_correct=is_correct,
                        selected_option=question.correct_option if is_correct else (question.correct_option + 1) % 4,
                        attempted_at=attempt_time,
                        time_taken_ms=18000 + (i * 2000),  # Normal time
                        confidence_level=5 if not is_correct else 4,  # Very confident even when wrong
                        network_type="4g",
                        app_version="1.0.0"
                    ))
                
                elif pattern == "average":
                    # Eva: Mixed performance, average student
                    is_correct = i % 2 == 0  # 50% accuracy
                    attempts.append(Attempt(
                        user_id=student.id,
                        question_id=question.id,
                        is_correct=is_correct,
                        selected_option=question.correct_option if is_correct else (question.correct_option + 1) % 4,
                        attempted_at=attempt_time,
                        time_taken_ms=20000 + (i * 3000),  # 20-35 seconds
                        confidence_level=3 if is_correct else 2,
                        network_type="wifi",
                        app_version="1.0.0"
                    ))
        
        db.add_all(attempts)
        db.commit()
        print(f"✅ Created {len(attempts)} attempts with varied psychometric data")
        
        # Create an assignment
        assignment = Assignment(
            classroom_id=classroom.id,
            title="Week 1: Algebra & Geometry Practice",
            description="Complete all questions on algebra and geometry topics",
            subject="MATHEMATICS",
            topic="Algebra",
            difficulty="MEDIUM",
            due_date=datetime.utcnow() + timedelta(days=7)
        )
        db.add(assignment)
        db.commit()
        print(f"✅ Created assignment: {assignment.title}")
        
        print("\n" + "="*60)
        print("📊 SAMPLE DATA SUMMARY")
        print("="*60)
        print(f"Teacher: {teacher.full_name} (email: {teacher.email})")
        print(f"Classroom: {classroom.name}")
        print(f"Join Code: {classroom.join_code}")
        print(f"Students: {len(students)}")
        print(f"  - Alice Strong: High performer (80% accuracy)")
        print(f"  - Bob Guesser: Fast but inaccurate (guessing pattern)")
        print(f"  - Carol Struggles: Needs help (slow, low accuracy)")
        print(f"  - David Misconception: Confident but wrong (misconceptions)")
        print(f"  - Eva Average: Mixed performance (50% accuracy)")
        print(f"Questions: {len(questions)} across 3 topics")
        print(f"Attempts: {len(attempts)} with psychometric data")
        print(f"Assignment: 1 active assignment")
        print("\n🎯 Use this data to test:")
        print("  - GET /api/v1/teacher/analytics/{classroom.id}")
        print("  - Guessing detection (<2s time_taken_ms)")
        print("  - Struggle detection (>60s time_taken_ms)")
        print("  - Misconception identification (confidence≥4 + wrong)")
        print("  - Per-topic performance breakdown")
        print("  - Class-wide averages")
        print("="*60)
        
        return {
            "teacher_id": teacher.id,
            "classroom_id": classroom.id,
            "join_code": classroom.join_code,
            "student_ids": [s.id for s, _ in students],
            "question_ids": [q.id for q in questions],
            "assignment_id": assignment.id
        }
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    result = create_sample_data()
    print(f"\n✨ Sample data created successfully!")
    print(f"   Classroom ID: {result['classroom_id']}")
    print(f"   Teacher ID: {result['teacher_id']}")
