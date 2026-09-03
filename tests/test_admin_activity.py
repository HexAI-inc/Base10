"""Tests for the admin audit log (AdminActivityLog + /admin/activity)."""
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.enums import UserRole
from app.models.admin_activity_log import AdminActivityLog
from app.core.security import create_access_token, get_password_hash


@pytest.fixture
def admin_user(session: Session):
    admin = User(
        phone_number="+23276000000",
        email="admin@example.com",
        full_name="Test Admin",
        hashed_password=get_password_hash("adminpass123"),
        is_active=True,
        is_verified=True,
        role=UserRole.ADMIN,
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)
    return admin


@pytest.fixture
def admin_headers(admin_user):
    token = create_access_token({"sub": str(admin_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_deactivate_user_writes_audit_log(client: AsyncClient, admin_headers, admin_user, test_user, session: Session):
    response = await client.put(
        f"/api/v1/admin/users/{test_user.id}/deactivate",
        params={"reason": "spamming"},
        headers=admin_headers,
    )
    assert response.status_code == 200

    log = session.query(AdminActivityLog).filter(
        AdminActivityLog.action_type == "user.deactivate"
    ).first()
    assert log is not None
    assert log.admin_id == admin_user.id
    assert log.target_id == test_user.id
    assert "spamming" in log.action_description


@pytest.mark.asyncio
async def test_role_change_writes_audit_log(client: AsyncClient, admin_headers, admin_user, test_user, session: Session):
    response = await client.post(
        f"/api/v1/admin/admin/users/{test_user.id}/role",
        json={"new_role": "teacher", "reason": "promotion"},
        headers=admin_headers,
    )
    assert response.status_code == 200

    log = session.query(AdminActivityLog).filter(
        AdminActivityLog.action_type == "user.role_change"
    ).first()
    assert log is not None
    assert log.metadata_json["new_role"] == "teacher"


@pytest.mark.asyncio
async def test_activity_endpoint_returns_logged_actions(client: AsyncClient, admin_headers, admin_user, test_user, session: Session):
    await client.put(
        f"/api/v1/admin/users/{test_user.id}/deactivate",
        params={"reason": "test"},
        headers=admin_headers,
    )
    await client.put(f"/api/v1/admin/users/{test_user.id}/activate", headers=admin_headers)

    response = await client.get("/api/v1/admin/activity", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["activities"]) == 2
    assert data["activities"][0]["admin_name"] == "Test Admin"
    # Most recent first
    assert data["activities"][0]["action_type"] == "user.activate"


@pytest.mark.asyncio
async def test_activity_endpoint_filters_by_action_type(client: AsyncClient, admin_headers, admin_user, test_user, session: Session):
    await client.put(
        f"/api/v1/admin/users/{test_user.id}/deactivate",
        params={"reason": "test"},
        headers=admin_headers,
    )
    await client.put(f"/api/v1/admin/users/{test_user.id}/activate", headers=admin_headers)

    response = await client.get(
        "/api/v1/admin/activity",
        params={"action_type": "user.deactivate"},
        headers=admin_headers,
    )
    data = response.json()
    assert data["total"] == 1
    assert data["activities"][0]["action_type"] == "user.deactivate"
