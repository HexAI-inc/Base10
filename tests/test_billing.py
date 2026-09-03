"""Tests for HPG billing integration."""
import hashlib
import hmac
import json
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.core.config import settings
from app.models.transaction import Transaction


class FakeHPGResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload
        self.text = json.dumps(payload)

    def json(self):
        return self._payload


@pytest.fixture(autouse=True)
def hpg_settings(monkeypatch):
    """Point billing at a fake HPG configuration for every test in this file."""
    monkeypatch.setattr(settings, "HPG_API_KEY", "sk_test_fake")
    monkeypatch.setattr(settings, "HPG_WEBHOOK_SECRET", "whsec_fake")


def sign(body: bytes) -> str:
    return hmac.new(settings.HPG_WEBHOOK_SECRET.encode("utf-8"), body, hashlib.sha256).hexdigest()


@pytest.mark.asyncio
async def test_initialize_creates_pending_transaction(client: AsyncClient, auth_headers: dict, test_db):
    fake_response = FakeHPGResponse(200, {
        "transaction_id": "tx_abc123",
        "status": "PENDING",
        "redirect_url": "https://pay.hpg.hexai.gm/checkout/abc123",
        "provider": "WAVE",
        "created_at": "2026-09-03T00:00:00Z",
    })

    with patch("app.api.v1.billing._hpg_initiate_collection", new=AsyncMock(return_value=fake_response)):
        response = await client.post(
            "/api/v1/billing/initialize",
            json={
                "plan_id": "premium",
                "email": "student@example.com",
                "currency": "GMD",
                "success_url": "https://base10.gm/billing/success",
                "error_url": "https://base10.gm/billing/error",
            },
            headers=auth_headers,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["transaction_id"] == "tx_abc123"
    assert data["redirect_url"] == "https://pay.hpg.hexai.gm/checkout/abc123"

    transaction = test_db.query(Transaction).filter(Transaction.client_reference.isnot(None)).first()
    assert transaction is not None
    assert transaction.status == "PENDING"
    assert transaction.plan_id == "premium"


@pytest.mark.asyncio
async def test_initialize_rejects_free_plan(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/v1/billing/initialize",
        json={
            "plan_id": "free",
            "email": "student@example.com",
            "success_url": "https://base10.gm/success",
            "error_url": "https://base10.gm/error",
        },
        headers=auth_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_webhook_valid_signature_activates_subscription(client: AsyncClient, auth_headers: dict, test_db, test_user):
    transaction = Transaction(
        client_reference="base10_1_999",
        transaction_id="tx_xyz",
        user_id=test_user.id,
        plan_id="premium",
        amount="500",
        currency="GMD",
        provider="WAVE",
        status="PENDING",
    )
    test_db.add(transaction)
    test_db.commit()

    payload = {
        "event": "payment.succeeded",
        "data": {
            "id": "tx_xyz",
            "type": "collection",
            "reference": "base10_1_999",
            "amount": "500",
            "currency": "GMD",
            "status": "SUCCEEDED",
            "provider": "WAVE",
            "environment": "TEST",
            "completed_at": "2026-09-03T00:05:00Z",
        },
    }
    body = json.dumps(payload).encode("utf-8")
    signature = sign(body)

    response = await client.post(
        "/api/v1/billing/webhook",
        content=body,
        headers={"x-hexai-signature": signature, "Content-Type": "application/json"},
    )
    assert response.status_code == 200

    test_db.refresh(transaction)
    assert transaction.status == "SUCCEEDED"

    test_db.refresh(test_user)
    assert test_user.subscription_plan == "premium"
    assert test_user.subscription_status == "active"
    assert test_user.subscription_expires_at is not None


@pytest.mark.asyncio
async def test_webhook_invalid_signature_rejected(client: AsyncClient):
    payload = {"event": "payment.succeeded", "data": {"reference": "does-not-matter"}}
    body = json.dumps(payload).encode("utf-8")

    response = await client.post(
        "/api/v1/billing/webhook",
        content=body,
        headers={"x-hexai-signature": "not-a-real-signature", "Content-Type": "application/json"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_webhook_is_idempotent(client: AsyncClient, test_db, test_user):
    transaction = Transaction(
        client_reference="base10_1_111",
        transaction_id="tx_idem",
        user_id=test_user.id,
        plan_id="premium",
        amount="500",
        currency="GMD",
        provider="WAVE",
        status="PENDING",
    )
    test_db.add(transaction)
    test_db.commit()

    payload = {
        "event": "payment.succeeded",
        "data": {"id": "tx_idem", "reference": "base10_1_111", "status": "SUCCEEDED"},
    }
    body = json.dumps(payload).encode("utf-8")
    signature = sign(body)
    headers = {"x-hexai-signature": signature, "Content-Type": "application/json"}

    first = await client.post("/api/v1/billing/webhook", content=body, headers=headers)
    assert first.status_code == 200

    test_db.refresh(test_user)
    expires_after_first = test_user.subscription_expires_at

    second = await client.post("/api/v1/billing/webhook", content=body, headers=headers)
    assert second.status_code == 200

    test_db.refresh(test_user)
    assert test_user.subscription_expires_at == expires_after_first


@pytest.mark.asyncio
async def test_get_transactions_lists_own_history(client: AsyncClient, auth_headers: dict, test_db, test_user):
    transaction = Transaction(
        client_reference="base10_1_222",
        transaction_id="tx_list",
        user_id=test_user.id,
        plan_id="premium",
        amount="500",
        currency="GMD",
        provider="WAVE",
        status="SUCCEEDED",
    )
    test_db.add(transaction)
    test_db.commit()

    response = await client.get("/api/v1/billing/transactions", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["transactions"]) == 1
    assert data["transactions"][0]["client_reference"] == "base10_1_222"


@pytest.mark.asyncio
async def test_cancel_subscription_updates_status(client: AsyncClient, auth_headers: dict, test_db, test_user):
    test_user.subscription_plan = "premium"
    test_user.subscription_status = "active"
    test_db.commit()

    response = await client.post("/api/v1/billing/cancel", headers=auth_headers)
    assert response.status_code == 200

    test_db.refresh(test_user)
    assert test_user.subscription_status == "cancelled"
