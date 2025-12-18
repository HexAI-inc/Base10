"""Marketing and Waitlist models."""
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from app.db.base import Base

class WaitlistLead(Base):
    """
    Waitlist leads for marketing and pre-launch engagement.
    
    Used to capture interest from landing pages before users create full accounts.
    """
    __tablename__ = "waitlist_leads"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, nullable=True)
    
    # Demographics
    school_name = Column(String, nullable=True)
    education_level = Column(String, nullable=True)
    location = Column(String, nullable=True)
    device_type = Column(String, nullable=True) # Android, iPhone, Laptop, etc.
    
    # Growth Hacking
    referral_source = Column(String, nullable=True) # e.g., "Facebook", "Friend", "WhatsApp"
    is_converted = Column(Boolean, default=False) # True once they actually register an account
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<WaitlistLead {self.phone_number} name={self.full_name}>"
