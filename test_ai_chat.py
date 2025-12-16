import asyncio
import httpx
import json

BASE_URL = "https://stingray-app-x7lzo.ondigitalocean.app"

async def test_ai_chat():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Login with existing user
        login_data = {"username": "esjallow03@gmail.com", "password": "Student@123"}
        response = await client.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
        if response.status_code != 200:
            print(f"Login failed: {response.text}")
            return

        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get a question ID (assuming there's at least one)
        response = await client.get(f"{BASE_URL}/api/v1/questions/", headers=headers)
        if response.status_code != 200 or not response.json():
            print(f"Failed to get questions: {response.text}")
            return

        question_id = response.json()[0]["id"]

        # Test AI chat
        chat_data = {
            "question_id": question_id,
            "message": "Can you explain how to solve 2x + 5 = 15 step by step?",
            "context": "Student is struggling with basic algebra equations"
        }
        response = await client.post(f"{BASE_URL}/api/v1/ai/chat", json=chat_data, headers=headers)
        print(f"Chat response status: {response.status_code}")
        print(f"Chat response: {response.json()}")

if __name__ == "__main__":
    asyncio.run(test_ai_chat())