"""
Quick tests for the 3 strategic endpoint additions.
Tests basic functionality without requiring external services.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ==================== AI ENDPOINTS TESTS ====================

def test_ai_status_unauthenticated():
    """AI status should require authentication."""
    response = client.get("/api/v1/ai/status")
    assert response.status_code == 401


def test_ai_explain_endpoint_exists():
    """AI explain endpoint should exist."""
    response = client.post("/api/v1/ai/explain", json={})
    # Should fail with 401 (auth) or 422 (validation), not 404
    assert response.status_code in [401, 422]


def test_ai_chat_endpoint_exists():
    """AI chat endpoint should exist."""
    response = client.post("/api/v1/ai/chat", json={})
    # Should fail with 401 (auth) or 422 (validation), not 404
    assert response.status_code in [401, 422]


# ==================== ASSETS ENDPOINTS TESTS ====================

def test_assets_image_requires_auth():
    """Image serving should require authentication."""
    response = client.get("/api/v1/assets/image/test.png")
    assert response.status_code == 401


def test_assets_image_info_requires_auth():
    """Image info should require authentication."""
    response = client.get("/api/v1/assets/image/test.png/info")
    assert response.status_code == 401


def test_assets_data_usage_requires_auth():
    """Data usage endpoint should require authentication."""
    response = client.get("/api/v1/assets/data-usage")
    assert response.status_code == 401


# ==================== BILLING ENDPOINTS TESTS ====================

def test_billing_plans_public():
    """Plans endpoint should be public (no auth required)."""
    response = client.get("/api/v1/billing/plans")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3  # free, premium, school
    
    # Verify plan structure
    plan = data[0]
    assert "id" in plan
    assert "name" in plan
    assert "price" in plan
    assert "features" in plan


def test_billing_plans_has_free_plan():
    """Should have a free plan."""
    response = client.get("/api/v1/billing/plans")
    data = response.json()
    
    free_plan = next((p for p in data if p["id"] == "free"), None)
    assert free_plan is not None
    assert free_plan["price"] == 0
    assert "Basic" in free_plan["name"]


def test_billing_plans_has_premium_plan():
    """Should have a premium plan."""
    response = client.get("/api/v1/billing/plans")
    data = response.json()
    
    premium_plan = next((p for p in data if p["id"] == "premium"), None)
    assert premium_plan is not None
    assert premium_plan["price"] == 500  # ₦500
    assert "Exam Master" in premium_plan["name"]


def test_billing_plans_has_school_plan():
    """Should have a school plan."""
    response = client.get("/api/v1/billing/plans")
    data = response.json()
    
    school_plan = next((p for p in data if p["id"] == "school"), None)
    assert school_plan is not None
    assert school_plan["price"] == 50000  # ₦50,000
    assert "School" in school_plan["name"]


def test_billing_get_specific_plan():
    """Should get specific plan by ID."""
    response = client.get("/api/v1/billing/plans/premium")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "premium"
    assert data["price"] == 500


def test_billing_get_invalid_plan():
    """Should return 404 for invalid plan."""
    response = client.get("/api/v1/billing/plans/nonexistent")
    assert response.status_code == 404


def test_billing_initialize_requires_auth():
    """Initialize payment should require authentication."""
    response = client.post("/api/v1/billing/initialize", json={
        "plan_id": "premium",
        "email": "test@example.com"
    })
    assert response.status_code == 401


def test_billing_webhook_accepts_post():
    """Webhook should accept POST requests."""
    response = client.post("/api/v1/billing/webhook", json={
        "event": "charge.success",
        "data": {}
    })
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_billing_subscription_requires_auth():
    """Subscription status should require authentication."""
    response = client.get("/api/v1/billing/subscription")
    assert response.status_code == 401


# ==================== INTEGRATION TEST ====================

def test_all_strategic_endpoints_registered():
    """Verify all 13 new endpoints are registered."""
    
    # AI endpoints (3)
    assert client.get("/api/v1/ai/status").status_code != 404
    assert client.post("/api/v1/ai/explain", json={}).status_code != 404
    assert client.post("/api/v1/ai/chat", json={}).status_code != 404
    
    # Assets endpoints (3)
    assert client.get("/api/v1/assets/image/test.png").status_code != 404
    assert client.get("/api/v1/assets/image/test.png/info").status_code != 404
    assert client.get("/api/v1/assets/data-usage").status_code != 404
    
    # Billing endpoints (7)
    assert client.get("/api/v1/billing/plans").status_code != 404
    assert client.get("/api/v1/billing/plans/premium").status_code != 404
    assert client.post("/api/v1/billing/initialize", json={}).status_code != 404
    assert client.post("/api/v1/billing/webhook", json={}).status_code != 404
    assert client.get("/api/v1/billing/subscription").status_code != 404
    assert client.post("/api/v1/billing/cancel").status_code != 404
    assert client.get("/api/v1/billing/transactions").status_code != 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
