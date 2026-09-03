"""Tests for the email-delivered account verification flow (interim SMS replacement)."""
from unittest.mock import patch

import pytest
from httpx import AsyncClient

from app.models.otp import OTP
from app.models.enums import OTPType


@pytest.mark.asyncio
async def test_send_verification_code_requires_email(client: AsyncClient, auth_headers: dict, test_user, test_db):
    test_user.email = None
    test_db.commit()

    response = await client.post("/api/v1/auth/send-verification-code", headers=auth_headers)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_send_verification_code_creates_otp_and_emails_it(client: AsyncClient, auth_headers: dict, test_user, test_db):
    test_user.is_verified = False
    test_db.commit()

    with patch("app.services.comms_service.CommunicationService._send_email", return_value=True) as mock_send:
        response = await client.post("/api/v1/auth/send-verification-code", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["dev_code"] is not None
    mock_send.assert_called_once()

    otp = test_db.query(OTP).filter(
        OTP.user_id == test_user.id,
        OTP.purpose == OTPType.PHONE_VERIFY
    ).first()
    assert otp is not None
    assert otp.code == data["dev_code"]


@pytest.mark.asyncio
async def test_verify_code_success(client: AsyncClient, auth_headers: dict, test_user, test_db):
    test_user.is_verified = False
    test_db.commit()

    with patch("app.services.comms_service.CommunicationService._send_email", return_value=True):
        send_response = await client.post("/api/v1/auth/send-verification-code", headers=auth_headers)
    code = send_response.json()["dev_code"]

    response = await client.post(
        "/api/v1/auth/verify-code",
        json={"code": code},
        headers=auth_headers,
    )
    assert response.status_code == 200

    test_db.refresh(test_user)
    assert test_user.is_verified is True
    assert test_user.verified_at is not None


@pytest.mark.asyncio
async def test_verify_code_wrong_code_rejected(client: AsyncClient, auth_headers: dict, test_user, test_db):
    test_user.is_verified = False
    test_db.commit()

    with patch("app.services.comms_service.CommunicationService._send_email", return_value=True):
        await client.post("/api/v1/auth/send-verification-code", headers=auth_headers)

    response = await client.post(
        "/api/v1/auth/verify-code",
        json={"code": "0000"},
        headers=auth_headers,
    )
    assert response.status_code == 400

    test_db.refresh(test_user)
    assert test_user.is_verified is False


@pytest.mark.asyncio
async def test_verify_code_without_sending_first_rejected(client: AsyncClient, auth_headers: dict, test_user, test_db):
    test_user.is_verified = False
    test_db.commit()

    response = await client.post(
        "/api/v1/auth/verify-code",
        json={"code": "1234"},
        headers=auth_headers,
    )
    assert response.status_code == 400
