"""
Manual test script for teacher analytics endpoint.
Creates test data and verifies analytics calculations.
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_teacher_analytics():
    """Test teacher analytics endpoint with comprehensive data."""
    
    print("🧪 Testing Teacher Analytics Endpoint")
    print("=" * 60)
    
    # 1. Register and login as teacher
    print("\n1️⃣  Creating teacher account...")
    teacher_data = {
        "phone_number": "+1555TEST01",
        "email": "test_teacher@analytics.test",
        "password": "TestPass123!",
        "full_name": "Analytics Test Teacher",
        "country_code": "NG"
    }
    
    register_response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=teacher_data)
    if register_response.status_code in [200, 201]:
        print("✅ Teacher registered successfully")
    else:
        # Try login if already exists
        print("⚠️  Registration failed, trying login...")
    
    login_response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        data={
            "username": teacher_data["phone_number"],
            "password": teacher_data["password"]
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    teacher_token = login_response.json()["access_token"]
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
    print(f"✅ Teacher logged in successfully")
    
    # 2. Create classroom
    print("\n2️⃣  Creating classroom...")
    classroom_response = requests.post(
        f"{BASE_URL}/api/v1/teacher/classrooms",
        json={
            "name": "Analytics Test Classroom",
            "description": "Testing psychometric analytics"
        },
        headers=teacher_headers
    )
    
    if classroom_response.status_code not in [200, 201]:
        print(f"❌ Failed to create classroom: {classroom_response.status_code}")
        print(classroom_response.text)
        return
    
    classroom = classroom_response.json()
    classroom_id = classroom["id"]
    join_code = classroom["join_code"]
    print(f"✅ Classroom created: ID {classroom_id}, Join Code: {join_code}")
    
    # 3. Create students and have them join
    print("\n3️⃣  Creating and enrolling students...")
    students = []
    student_patterns = [
        ("Guesser", "guesser"),
        ("Struggler", "struggler"),
        ("Strong", "strong")
    ]
    
    for i, (name, pattern) in enumerate(student_patterns):
        student_data = {
            "phone_number": f"+1555TEST{10+i}",
            "email": f"student_{pattern}@test.com",
            "password": "StudentPass123!",
            "full_name": f"Test {name}",
            "country_code": "NG"
        }
        
        # Register student
        requests.post(f"{BASE_URL}/api/v1/auth/register", json=student_data)
        
        # Login student
        student_login = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            data={
                "username": student_data["phone_number"],
                "password": student_data["password"]
            }
        )
        
        if student_login.status_code == 200:
            student_token = student_login.json()["access_token"]
            student_headers = {"Authorization": f"Bearer {student_token}"}
            student_id = student_login.json()["user"]["id"]
            
            # Join classroom
            join_response = requests.post(
                f"{BASE_URL}/api/v1/teacher/classrooms/join",
                json={"join_code": join_code},
                headers=student_headers
            )
            
            if join_response.status_code == 200:
                students.append((student_id, pattern, student_headers))
                print(f"✅ {name} enrolled (pattern: {pattern})")
            else:
                print(f"⚠️  {name} failed to join: {join_response.status_code}")
        else:
            print(f"⚠️  {name} login failed")
    
    # 4. Get random questions
    print("\n4️⃣  Fetching questions...")
    questions_response = requests.get(
        f"{BASE_URL}/api/v1/questions/random?limit=5",
        headers=teacher_headers
    )
    
    if questions_response.status_code != 200:
        print(f"❌ Failed to fetch questions: {questions_response.status_code}")
        return
    
    questions = questions_response.json()
    print(f"✅ Retrieved {len(questions)} questions")
    
    # 5. Create attempts with psychometric patterns
    print("\n5️⃣  Creating attempts with varied psychometric data...")
    
    for student_id, pattern, student_headers in students:
        attempts = []
        
        for i, question in enumerate(questions):
            if pattern == "guesser":
                # Fast, low confidence, poor accuracy
                attempts.append({
                    "question_id": question["id"],
                    "is_correct": i % 3 == 0,  # 33% accuracy
                    "selected_option": (question["correct_option"] + i) % 4,
                    "attempted_at": datetime.utcnow().isoformat(),
                    "time_taken_ms": 1500,  # <2s = guessing
                    "confidence_level": 1 if i % 2 == 0 else 2,
                    "network_type": "3g",
                    "app_version": "1.0.0"
                })
            
            elif pattern == "struggler":
                # Slow, low confidence, poor accuracy
                attempts.append({
                    "question_id": question["id"],
                    "is_correct": i % 4 == 0,  # 25% accuracy
                    "selected_option": (question["correct_option"] + 2) % 4,
                    "attempted_at": datetime.utcnow().isoformat(),
                    "time_taken_ms": 75000,  # >60s = struggling
                    "confidence_level": 2,
                    "network_type": "2g",
                    "app_version": "0.9.5"
                })
            
            else:  # strong
                # Normal time, appropriate confidence, good accuracy
                attempts.append({
                    "question_id": question["id"],
                    "is_correct": i < 4,  # 80% accuracy
                    "selected_option": question["correct_option"] if i < 4 else (question["correct_option"] + 1) % 4,
                    "attempted_at": datetime.utcnow().isoformat(),
                    "time_taken_ms": 15000 + (i * 2000),  # 15-23s
                    "confidence_level": 4 if i < 4 else 3,
                    "network_type": "wifi",
                    "app_version": "1.0.0"
                })
        
        # Sync attempts
        sync_response = requests.post(
            f"{BASE_URL}/api/v1/sync/push",
            json={
                "attempts": attempts,
                "device_id": f"device_{student_id}"
            },
            headers=student_headers
        )
        
        if sync_response.status_code == 200:
            print(f"✅ Synced {len(attempts)} attempts for {pattern}")
        else:
            print(f"⚠️  Sync failed for {pattern}: {sync_response.status_code}")
    
    # 6. Test analytics endpoint
    print("\n6️⃣  Testing analytics endpoint...")
    analytics_response = requests.get(
        f"{BASE_URL}/api/v1/teacher/analytics/{classroom_id}",
        headers=teacher_headers
    )
    
    if analytics_response.status_code != 200:
        print(f"❌ Analytics request failed: {analytics_response.status_code}")
        print(analytics_response.text)
        return
    
    analytics = analytics_response.json()
    
    # Display results
    print("\n" + "=" * 60)
    print("📊 ANALYTICS RESULTS")
    print("=" * 60)
    print(f"Classroom ID: {analytics['classroom_id']}")
    print(f"Total Students: {analytics['total_students']}")
    print(f"Active Students (7 days): {analytics['active_students']}")
    print(f"Class Accuracy: {analytics.get('class_accuracy', 0):.1f}%")
    print(f"Average Confidence: {analytics.get('average_confidence', 0):.1f}")
    
    print("\n👥 Student Performance:")
    for student_perf in analytics.get('student_performance', []):
        print(f"\n  Student ID: {student_perf['student_id']}")
        print(f"  - Total Attempts: {student_perf['total_attempts']}")
        print(f"  - Accuracy: {student_perf['accuracy']:.1f}%")
        print(f"  - Guessing Rate: {student_perf['guessing_rate']:.1f}%")
        print(f"  - Struggle Rate: {student_perf['struggle_rate']:.1f}%")
        print(f"  - Misconceptions: {student_perf['misconception_count']}")
        print(f"  - Avg Confidence: {student_perf.get('average_confidence', 0):.1f}")
    
    print("\n📚 Topic Performance:")
    for topic_perf in analytics.get('topic_performance', []):
        print(f"\n  Topic: {topic_perf['topic']}")
        print(f"  - Attempts: {topic_perf['total_attempts']}")
        print(f"  - Accuracy: {topic_perf['accuracy']:.1f}%")
        print(f"  - Avg Confidence: {topic_perf.get('average_confidence', 0):.1f}")
        print(f"  - Struggling Students: {topic_perf.get('struggling_students', 0)}")
    
    # Verify psychometric detection
    print("\n" + "=" * 60)
    print("🔍 PSYCHOMETRIC VERIFICATION")
    print("=" * 60)
    
    # Find guesser, struggler, and strong student
    student_perfs = {sp['student_id']: sp for sp in analytics.get('student_performance', [])}
    
    for student_id, pattern, _ in students:
        if student_id in student_perfs:
            perf = student_perfs[student_id]
            print(f"\n{pattern.upper()}:")
            
            if pattern == "guesser":
                if perf['guessing_rate'] > 50:
                    print(f"  ✅ Correctly detected high guessing rate: {perf['guessing_rate']:.1f}%")
                else:
                    print(f"  ⚠️  Expected high guessing rate, got: {perf['guessing_rate']:.1f}%")
            
            elif pattern == "struggler":
                if perf['struggle_rate'] > 50:
                    print(f"  ✅ Correctly detected high struggle rate: {perf['struggle_rate']:.1f}%")
                else:
                    print(f"  ⚠️  Expected high struggle rate, got: {perf['struggle_rate']:.1f}%")
            
            else:  # strong
                if perf['accuracy'] > 70:
                    print(f"  ✅ Correctly identified strong performance: {perf['accuracy']:.1f}% accuracy")
                else:
                    print(f"  ⚠️  Expected high accuracy, got: {perf['accuracy']:.1f}%")
    
    print("\n" + "=" * 60)
    print("✅ Analytics test complete!")
    print("=" * 60)
    
    return analytics


if __name__ == "__main__":
    try:
        analytics = test_teacher_analytics()
        if analytics:
            print("\n✨ Full analytics data:")
            print(json.dumps(analytics, indent=2))
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
