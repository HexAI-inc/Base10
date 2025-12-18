"""Account recovery endpoints for password reset."""
import random
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.session import get_db
from app.models.user import User
from app.models.otp import OTP
from app.core.security import get_password_hash
from app.services.comms_service import CommunicationService, MessageType, MessagePriority

router = APIRouter()
comms = CommunicationService()


# Request schemas
class ForgotPasswordRequest(BaseModel):
    identifier: str  # Phone number or email

class ResetPasswordRequest(BaseModel):
    identifier: str  # Phone number or email
    otp_code: str    # 4-digit code
    new_password: str


@router.post("/forgot-password", status_code=200)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Generate OTP for password reset.
    
    Flow:
    1. User provides phone/email
    2. System generates 4-digit OTP
    3. OTP sent via SMS/Email (handled by notification service)
    4. Returns success (don't reveal if user exists for security)
    """
    # Find user by phone or email
    user = db.query(User).filter(
        (User.phone_number == request.identifier) | 
        (User.email == request.identifier)
    ).first()
    
    if not user:
        # Security: Don't reveal if user exists
        return {
            "message": "If that account exists, we've sent a reset code",
            "expires_in_minutes": 15
        }
    
    # Invalidate any existing OTPs for this user
    db.query(OTP).filter(
        OTP.user_id == user.id,
        OTP.purpose == "password_reset",
        OTP.is_used == False
    ).update({"is_used": True})
    
    # Generate 4-digit OTP
    otp_code = f"{random.randint(1000, 9999)}"
    
    # Create OTP record
    otp = OTP(
        user_id=user.id,
        code=otp_code,
        purpose="password_reset",
        expires_at=datetime.utcnow() + timedelta(minutes=15)
    )
    db.add(otp)
    db.commit()
    
    # Trigger notification via Comms Service
    comms.send_notification(
        user_id=user.id,
        message_type=MessageType.PASSWORD_RESET,
        priority=MessagePriority.CRITICAL,
        title="Base10 Password Reset",
        body=f"Your Base10 verification code is: {otp_code}. Valid for 15 minutes.",
        user_phone=user.phone_number,
        user_email=user.email,
        has_app_installed=False # Force SMS/Email for recovery
    )
    
    return {
        "message": "If that account exists, we've sent a reset code",
        "expires_in_minutes": 15,
        # DEVELOPMENT ONLY - remove in production
        "dev_otp": otp_code if user.phone_number else None
    }


@router.post("/reset-password", status_code=200)
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Reset password using OTP.
    
    Flow:
    1. User provides identifier + OTP + new password
    2. Verify OTP is valid
    3. Update password
    4. Invalidate OTP
    """
    # Find user
    user = db.query(User).filter(
        (User.phone_number == request.identifier) | 
        (User.email == request.identifier)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials"
        )
    
    # Find valid OTP
    otp = db.query(OTP).filter(
        OTP.user_id == user.id,
        OTP.code == request.otp_code,
        OTP.purpose == "password_reset",
        OTP.is_used == False
    ).first()
    
    if not otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired code"
        )
    
    # Check if OTP is still valid
    if not otp.is_valid():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code has expired or exceeded max attempts"
        )
    
    # Increment attempts
    otp.attempts += 1
    
    # Verify OTP code
    if otp.code != request.otp_code:
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid code. {otp.max_attempts - otp.attempts} attempts remaining"
        )
    
    # Update password
    user.hashed_password = get_password_hash(request.new_password)
    
    # Mark OTP as used
    otp.is_used = True
    otp.used_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Password reset successful",
        "user_id": user.id
    }


@router.post("/verify-otp", status_code=200)
async def verify_otp(
    identifier: str,
    otp_code: str,
    db: Session = Depends(get_db)
):
    """
    Verify OTP without resetting password (for phone verification).
    """
    user = db.query(User).filter(
        (User.phone_number == identifier) | 
        (User.email == identifier)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials"
        )
    
    otp = db.query(OTP).filter(
        OTP.user_id == user.id,
        OTP.code == otp_code,
        OTP.is_used == False
    ).first()
    
    if not otp or not otp.is_valid():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired code"
        )
    
    # Mark as verified
    user.is_verified = True
    otp.is_used = True
    otp.used_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Verification successful",
        "user_id": user.id
    }
