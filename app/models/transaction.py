"""Transaction model for HPG (HexAI Payment Gateway) billing."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base


class Transaction(Base):
    """
    A payment transaction against HPG's /collections API.

    Tracked from the moment we call /collections/initiate (status
    PENDING) through webhook confirmation (SUCCEEDED/FAILED/EXPIRED/
    CANCELLED), keyed by client_reference so webhook processing is
    idempotent.
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    client_reference = Column(String(100), unique=True, index=True, nullable=False)
    transaction_id = Column(String(100), nullable=True)  # HPG's own id, set once known

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(String(50), nullable=False)

    amount = Column(String(20), nullable=False)  # HPG amounts are decimal strings
    currency = Column(String(10), nullable=False)
    provider = Column(String(20), nullable=False, default="WAVE")  # WAVE, APS, WAYCHIT_CARD
    status = Column(String(20), nullable=False, default="PENDING")  # PENDING/SUCCEEDED/FAILED/EXPIRED/CANCELLED

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<Transaction {self.client_reference} {self.status}>"
