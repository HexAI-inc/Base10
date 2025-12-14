"""Test authentication flow."""
import pytest
from httpx import AsyncClient
from jose import jwt
from app.core.config import settings


@pytest.mark.asyncio
async def test_login_flow(client: AsyncClient, test_user, test_db):
    """Test complete login flow."""
    # Step 1: Try to login
    login_data = {
        "username": test_user.phone_number,
        "password": "testpass123"
    }
    response = await client.post("/api/v1/auth/login", data=login_data)
    
    print(f"\n=== Login Response ===")
    print(f"Status: {response.status_code}")
    
    assert response.status_code == 200, f"Login failed: {response.text}"
    
    # Step 2: Extract and decode token
    data = response.json()
    assert "access_token" in data
    token = data["access_token"]
    
    # Decode token to see payload
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    print(f"Decoded token: {decoded}")
    print(f"User ID in token: {decoded.get('sub')}")
    
    # Verify user exists in test DB
    from app.models.user import User
    user_in_db = test_db.query(User).filter(User.id == decoded.get('sub')).first()
    print(f"User in test DB: {user_in_db}")
    print(f"User phone: {user_in_db.phone_number if user_in_db else 'NOT FOUND'}")
    
    # Step 3: Use token to access protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    me_response = await client.get("/api/v1/auth/me", headers=headers)
    
    print(f"\n=== /me Response ===")
    print(f"Status: {me_response.status_code}")
    print(f"Body: {me_response.text}")
    
    assert me_response.status_code == 200, f"/me failed: {me_response.text}"
    me_data = me_response.json()
    assert me_data["phone_number"] == test_user.phone_number
    
    print("\n✅ Auth flow works!")
