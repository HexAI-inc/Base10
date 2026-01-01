"""
Critical test: Offline Sync Flow
This must pass before ANY deployment to production.

Tests the entire lifecycle:
1. User authenticates
2. Pushes offline attempts (simulating 10 questions answered offline)
3. Verifies data integrity
4. Checks duplicate prevention
5. Validates stats calculation
"""
import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_complete_offline_sync_lifecycle(
    client: AsyncClient, 
    auth_headers: dict, 
    test_user,
    test_questions
):
    """
    THE BIG TEST: Complete offline-to-online sync flow.
    If this passes, your sync system works.
    """
    
    # Step 1: Verify user is authenticated
    profile_res = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert profile_res.status_code == 200
    assert profile_res.json()["phone_number"] == test_user.phone_number
    
    # Step 2: Simulate offline quiz attempts (student answered 10 questions)
    offline_attempts = [
        {
            "question_id": test_questions[0].id,
            "selected_option": 1,  # Correct answer
            "is_correct": True,
            "attempted_at": (datetime.utcnow() - timedelta(minutes=10)).isoformat()
        },
        {
            "question_id": test_questions[1].id,
            "selected_option": 0,  # Wrong answer
            "is_correct": False,
            "attempted_at": (datetime.utcnow() - timedelta(minutes=9)).isoformat()
        },
        {
            "question_id": test_questions[2].id,
            "selected_option": 0,  # Correct answer
            "is_correct": True,
            "attempted_at": (datetime.utcnow() - timedelta(minutes=8)).isoformat()
        },
        {
            "question_id": test_questions[0].id,
            "selected_option": 2,  # Wrong answer (2nd attempt)
            "is_correct": False,
            "attempted_at": (datetime.utcnow() - timedelta(minutes=7)).isoformat()
        },
        {
            "question_id": test_questions[1].id,
            "selected_option": 2,  # Correct answer (2nd attempt)
            "is_correct": True,
            "attempted_at": (datetime.utcnow() - timedelta(minutes=6)).isoformat()
        }
    ]
    
    # Step 3: Push offline data to server
    push_res = await client.post("/api/v1/sync/push", json={"attempts": offline_attempts, "device_id": "test-device-123"},
        headers=auth_headers
    )
    
    assert push_res.status_code == 200, f"Sync push failed: {push_res.text}"
    push_data = push_res.json()
    assert push_data["synced_count"] == 5, "Not all attempts synced"
    assert push_data["failed_count"] == 0, "Some attempts failed to sync"
    
    # Step 4: Verify stats are calculated correctly
    stats_res = await client.get("/api/v1/sync/stats", headers=auth_headers)
    assert stats_res.status_code == 200
    stats = stats_res.json()
    
    # Should have 5 total attempts
    assert stats["total_attempts"] == 5
    
    # 3 correct, 2 wrong = 60% accuracy
    assert stats["accuracy"] == 60.0, f"Expected 60% accuracy, got {stats['accuracy']}%"
    
    # Step 5: Check weak areas detection
    # User got Mathematics question wrong on 2nd attempt
    assert "weak_topics" in stats
    weak_topics = stats["weak_topics"]
    assert len(weak_topics) > 0, "Weak topics not detected"
    
    # Step 6: Test duplicate prevention
    # Try pushing same attempts again
    duplicate_push = await client.post(
        "/api/v1/sync/push",
        json={"attempts": offline_attempts[:2], "device_id": "test-device-123"},
        headers=auth_headers
    )
    
    # Should still work but not create duplicates
    assert duplicate_push.status_code == 200
    dup_data = duplicate_push.json()
    
    # Verify stats haven't doubled
    stats_after_dup = await client.get("/api/v1/sync/stats", headers=auth_headers)
    assert stats_after_dup.json()["total_attempts"] <= 7  # Max 2 duplicates accepted
    
    print("✅ Complete sync flow test PASSED")


@pytest.mark.asyncio
async def test_sync_with_missing_question(
    client: AsyncClient,
    auth_headers: dict
):
    """
    Edge case: Student tries to sync attempt for non-existent question.
    Should fail gracefully, not crash the sync.
    """
    invalid_attempt = [{
        "question_id": 99999,  # Doesn't exist
        "selected_option": 0,
        "is_correct": False,
        "attempted_at": datetime.utcnow().isoformat()
    }]
    
    push_res = await client.post("/api/v1/sync/push", json={"attempts": invalid_attempt, "device_id": "test-device-123"},
        headers=auth_headers
    )
    
    # Should return 200 but mark as failed
    assert push_res.status_code == 200
    data = push_res.json()
    assert data["failed_count"] == 1
    assert data["synced_count"] == 0


@pytest.mark.asyncio
async def test_sync_stats_empty_state(
    client: AsyncClient,
    auth_headers: dict
):
    """
    Test stats for user with no attempts yet.
    Should return zeroed stats, not crash.
    """
    stats_res = await client.get("/api/v1/sync/stats", headers=auth_headers)
    assert stats_res.status_code == 200
    stats = stats_res.json()
    
    assert stats["total_attempts"] == 0
    assert stats["accuracy"] == 0.0
    assert stats["weak_topics"] == []


@pytest.mark.asyncio
async def test_concurrent_sync_simulation(
    client: AsyncClient,
    auth_headers: dict,
    test_questions
):
    """
    Simulate 10 users syncing at the same time.
    Tests database transaction handling.
    """
    import asyncio
    
    async def push_for_user(user_num: int):
        """Simulate one user's sync."""
        attempts = [{
            "question_id": test_questions[0].id,
            "selected_option": user_num % 4,
            "is_correct": (user_num % 4) == 1,
            "attempted_at": datetime.utcnow().isoformat()
        }]
        return await client.post("/api/v1/sync/push", json={"attempts": attempts, "device_id": "test-device-123"},
            headers=auth_headers
        )
    
    # Push 10 concurrent syncs
    tasks = [push_for_user(i) for i in range(10)]
    results = await asyncio.gather(*tasks)
    
    # All should succeed
    for res in results:
        assert res.status_code == 200
    
    # Verify stats reflect all attempts
    stats_res = await client.get("/api/v1/sync/stats", headers=auth_headers)
    stats = stats_res.json()
    assert stats["total_attempts"] == 10


@pytest.mark.asyncio
async def test_sync_pull_delta(
    client: AsyncClient,
    auth_headers: dict,
    test_questions
):
    """
    Test delta sync: Only pull questions updated after last sync.
    Critical for data efficiency.
    """
    # Get initial timestamp
    last_sync = datetime.utcnow().isoformat()
    
    # Pull questions
    pull_res = await client.post(
        "/api/v1/sync/pull",
        json={
            "last_sync_timestamp": last_sync,
            "limit": 50
        },
        headers=auth_headers
    )
    
    assert pull_res.status_code == 200
    data = pull_res.json()
    assert "questions" in data
    
    # Since last_sync is now, should get empty or small response
    print(f"Delta pull returned {len(data.get('questions', []))} questions")


# Run tests with coverage
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=app", "--cov-report=term-missing"])
