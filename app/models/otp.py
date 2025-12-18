"""OTP (One-Time Password) model for account recovery."""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.enums import OTPType
from datetime import datetime, timedelta


class OTP(Base):
    """
    OTP tokens for password reset and verification.
    
    Design:
    - 4-digit codes for easy SMS entry
    - 15-minute expiry window
    - Max 3 attempts to prevent brute force
    - One-time use (is_used flag)
    """
    __tablename__ = "otps"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # OTP Details
    code = Column(String(4), nullable=False)  # 4-digit code
    purpose = Column(SQLEnum(OTPType), nullable=False)  # "password_reset" or "phone_verify"
    
    # Security
    is_used = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)  # Tracks failed verification attempts
    max_attempts = Column(Integer, default=3)
    
    # Timing
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="otps")
    
    def is_valid(self) -> bool:
        """Check if OTP is still valid."""
        if self.is_used:
            return False
        if self.attempts >= self.max_attempts:
            return False
        if datetime.utcnow() > self.expires_at:
            return False
        return True
    
    def __repr__(self):
        return f"<OTP user={self.user_id} purpose={self.purpose} valid={self.is_valid()}>"
