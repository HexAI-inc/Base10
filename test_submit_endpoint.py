#!/usr/bin/env python3
"""Test script for the new answer submission endpoint."""
import requests
import json
from datetime import datetime

# Test the answer submission endpoint
def test_submit_answer():
    # First, login to get a token
    login_url = "http://localhost:8000/api/v1/auth/login"
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }

    try:
        # Try to login
        login_response = requests.post(login_url, json=login_data)
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Login successful")
        else:
            print("❌ Login failed, trying to register...")
            # Try to register first
            register_url = "http://localhost:8000/api/v1/auth/register"
            register_data = {
                "email": "test@example.com",
                "password": "password123",
                "first_name": "Test",
                "last_name": "User",
                "phone": "+1234567890"
            }
            register_response = requests.post(register_url, json=register_data)
            if register_response.status_code in [200, 201]:  # Accept both 200 and 201
                print("✅ Registration successful, using returned token...")
                token = register_response.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}
                print("✅ Token obtained")
            else:
                print(f"❌ Registration failed: {register_response.status_code}")
                print(f"   Response: {register_response.text}")
                return

        # Get a question to answer
        questions_url = "http://localhost:8000/api/v1/questions/?limit=1"
        questions_response = requests.get(questions_url, headers=headers)

        if questions_response.status_code != 200:
            print(f"❌ Failed to get questions: {questions_response.text}")
            return

        questions = questions_response.json()
        if not questions:
            print("❌ No questions available")
            return

        question = questions[0]
        print(f"📚 Got question: {question['id']} - {question['question'][:50]}...")

        # Submit an answer
        submit_url = "http://localhost:8000/api/v1/questions/submit"
        attempt_data = {
            "question_id": question["id"],
            "selected_option": 0,  # Choose first option
            "is_correct": True,    # Assume correct for test
            "attempted_at": datetime.utcnow().isoformat(),
            "time_taken_ms": 5000,
            "confidence_level": 4
        }

        submit_response = requests.post(submit_url, json=attempt_data, headers=headers)

        if submit_response.status_code == 200:
            result = submit_response.json()
            print("✅ Answer submitted successfully!")
            print(f"   Attempt ID: {result['id']}")
            print(f"   Correct: {result['is_correct']}")
            print(f"   Question ID: {result['question_id']}")
        else:
            print(f"❌ Answer submission failed: {submit_response.status_code}")
            print(f"   Response: {submit_response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        print("   Start with: python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_submit_answer()