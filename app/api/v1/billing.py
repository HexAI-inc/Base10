"""
Billing and monetization endpoints.
Handles subscriptions and payments via HPG (HexAI Payment Gateway).
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, timedelta
import hashlib
import hmac
import httpx
from enum import Enum

from app.db.session import get_db
from app.models.user import User
from app.models.transaction import Transaction
from app.api.v1.auth import get_current_user
from app.core.config import settings


router = APIRouter()


async def _hpg_initiate_collection(payload: dict) -> httpx.Response:
    """Call HPG's POST /collections/initiate. Isolated for testability."""
    async with httpx.AsyncClient() as http_client:
        return await http_client.post(
            f"{settings.HPG_BASE_URL}/collections/initiate",
            json=payload,
            headers={"Authorization": f"Bearer {settings.HPG_API_KEY}"},
            timeout=15.0,
        )


class PlanType(str, Enum):
    """Subscription plan types."""
    FREE = "free"
    PREMIUM = "premium"
    SCHOOL = "school"


class Currency(str, Enum):
    """Supported currencies."""
    NGN = "NGN"  # Nigerian Naira
    GHS = "GHS"  # Ghanaian Cedi
    GMD = "GMD"  # Gambian Dalasi
    SLL = "SLL"  # Sierra Leonean Leone
    USD = "USD"  # US Dollar


class Plan(BaseModel):
    """Subscription plan details."""
    id: str = Field(..., description="Plan identifier")
    name: str = Field(..., description="Display name")
    description: str = Field(..., description="Plan features description")
    price: int = Field(..., description="Price in base currency units")
    currency: Currency = Field(default=Currency.GMD, description="Currency code")
    duration_days: int = Field(..., description="Plan duration in days")
    features: List[str] = Field(..., description="List of features included")
    is_popular: bool = Field(default=False, description="Mark as popular/recommended")


class InitializePaymentRequest(BaseModel):
    """Request to start a payment transaction."""
    plan_id: str = Field(..., description="The plan to subscribe to")
    email: EmailStr = Field(..., description="User's email for payment receipt")
    currency: Currency = Field(default=Currency.GMD, description="Payment currency")
    provider: str = Field(default="WAVE", description="Payment rail: WAVE, APS, or WAYCHIT_CARD")
    success_url: str = Field(..., description="Where to redirect the user after a successful payment")
    error_url: str = Field(..., description="Where to redirect the user after a failed payment")


class InitializePaymentResponse(BaseModel):
    """Response with HPG payment initialization details."""
    transaction_id: str = Field(..., description="HPG transaction identifier")
    status: str = Field(..., description="Initial transaction status (PENDING)")
    redirect_url: str = Field(..., description="URL to redirect the user to complete payment")
    provider: str = Field(..., description="Payment rail handling this transaction")
    created_at: str = Field(..., description="ISO timestamp from HPG")


# Define available plans
PLANS = [
    Plan(
        id="free",
        name="Basic",
        description="Essential features for exam preparation",
        price=0,
        currency=Currency.GMD,
        duration_days=365,
        features=[
            "Unlimited offline questions",
            "Basic flashcards",
            "Progress tracking",
            "5 AI explanations per day",
            "Standard image quality"
        ],
        is_popular=False
    ),
    Plan(
        id="premium",
        name="Exam Master",
        description="Advanced features for serious students",
        price=500,  # NOTE: value inherited from the old NGN pricing (~500 Naira/month, ~$0.50 USD) -
                    # currency below is now GMD but this number hasn't been repriced for GMD, needs a business decision
        currency=Currency.GMD,
        duration_days=30,
        features=[
            "Everything in Basic",
            "Unlimited AI chat",
            "Unlimited AI explanations",
            "High-quality images",
            "Priority sync",
            "Detailed analytics",
            "Ad-free experience"
        ],
        is_popular=True
    ),
    Plan(
        id="school",
        name="School License",
        description="Complete solution for educational institutions",
        price=50000,  # NOTE: inherited NGN pricing (~50,000 Naira/year), not yet repriced for GMD
        currency=Currency.GMD,
        duration_days=365,
        features=[
            "Everything in Premium",
            "Up to 500 student accounts",
            "Teacher dashboard access",
            "Class analytics",
            "Assignment management",
            "Bulk student enrollment",
            "Priority support",
            "Custom branding"
        ],
        is_popular=False
    )
]


@router.get("/plans", response_model=List[Plan])
async def get_plans(currency: Optional[Currency] = None):
    """
    List all available subscription plans.

    **Returns**: Array of plans with features and pricing

    **Use Case**: Display pricing page to users
    """
    # In production, could convert prices based on requested currency
    # For now, return all plans
    return PLANS


@router.get("/plans/{plan_id}", response_model=Plan)
async def get_plan(plan_id: str):
    """Get details for a specific plan."""
    plan = next((p for p in PLANS if p.id == plan_id), None)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.post("/initialize", response_model=InitializePaymentResponse)
async def initialize_payment(
    request: InitializePaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initialize a payment transaction with HPG.

    **Flow**:
    1. User selects a plan
    2. This endpoint creates a PENDING Transaction and calls HPG's
       /collections/initiate
    3. Returns the redirect_url for the user to complete payment
    4. HPG sends a webhook (or we poll /collections/status) to confirm
    """
    # Validate plan exists
    plan = next((p for p in PLANS if p.id == request.plan_id), None)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Free plan doesn't need payment
    if plan.price == 0:
        raise HTTPException(status_code=400, detail="Free plan doesn't require payment")

    if not settings.HPG_API_KEY:
        raise HTTPException(status_code=503, detail="Billing is not configured")

    # Generate unique client reference
    timestamp = int(datetime.utcnow().timestamp())
    client_reference = f"base10_{current_user.id}_{timestamp}"

    payload = {
        "amount": str(plan.price),
        "currency": request.currency.value,
        "customer_name": current_user.full_name or current_user.username or "Base10 Student",
        "customer_mobile": current_user.phone_number or "",
        "success_url": request.success_url,
        "error_url": request.error_url,
        "client_reference": client_reference,
        "provider": request.provider,
    }

    try:
        response = await _hpg_initiate_collection(payload)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Could not reach payment provider")

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Payment provider error: {response.text}"
        )

    hpg_data = response.json()

    transaction = Transaction(
        client_reference=client_reference,
        transaction_id=hpg_data.get("transaction_id"),
        user_id=current_user.id,
        plan_id=plan.id,
        amount=str(plan.price),
        currency=request.currency.value,
        provider=hpg_data.get("provider", request.provider),
        status=hpg_data.get("status", "PENDING"),
    )
    db.add(transaction)
    db.commit()

    return InitializePaymentResponse(
        transaction_id=hpg_data["transaction_id"],
        status=hpg_data.get("status", "PENDING"),
        redirect_url=hpg_data["redirect_url"],
        provider=hpg_data.get("provider", request.provider),
        created_at=hpg_data.get("created_at", datetime.utcnow().isoformat()),
    )


@router.post("/webhook")
async def payment_webhook(
    request: Request,
    x_hexai_signature: Optional[str] = Header(None, alias="x-hexai-signature"),
    wave_signature: Optional[str] = Header(None, alias="wave-signature"),
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint for HPG payment notifications.

    **Security**: Validates the HMAC-SHA256 signature (x-hexai-signature,
    legacy alias wave-signature) against the raw request body before
    processing.

    **Events Handled**:
    - `payment.succeeded` / `payment.failed` / `payment.expired` / `payment.cancelled`
    - `payout.*` events are acknowledged but not processed (payouts aren't
      used by this app)
    """
    body = await request.body()
    signature = x_hexai_signature or wave_signature

    if not settings.HPG_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Billing is not configured")

    if not signature:
        raise HTTPException(status_code=401, detail="Missing webhook signature")

    computed_signature = hmac.new(
        settings.HPG_WEBHOOK_SECRET.encode("utf-8"),
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_signature, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    event = payload.get("event", "")
    data = payload.get("data", {})

    if event.startswith("payout."):
        # Payouts aren't used by this app; acknowledge and skip.
        return {"status": "success", "message": "Webhook processed"}

    reference = data.get("reference")
    if not reference:
        return {"status": "success", "message": "Webhook processed"}

    transaction = db.query(Transaction).filter(
        Transaction.client_reference == reference
    ).first()

    if not transaction:
        return {"status": "success", "message": "Webhook processed"}

    # Idempotency: a terminal status is never overwritten by a redelivery.
    if transaction.status in ("SUCCEEDED", "FAILED", "EXPIRED", "CANCELLED"):
        return {"status": "success", "message": "Webhook processed"}

    new_status = data.get("status")
    completed_at = data.get("completed_at")

    if event == "payment.succeeded":
        transaction.status = "SUCCEEDED"
        transaction.transaction_id = data.get("id", transaction.transaction_id)
        transaction.completed_at = datetime.utcnow()

        user = db.query(User).filter(User.id == transaction.user_id).first()
        plan = next((p for p in PLANS if p.id == transaction.plan_id), None)
        if user and plan:
            user.subscription_plan = plan.id
            user.subscription_status = "active"
            user.subscription_expires_at = datetime.utcnow() + timedelta(days=plan.duration_days)

    elif event == "payment.failed":
        transaction.status = "FAILED"
    elif event == "payment.expired":
        transaction.status = "EXPIRED"
    elif event == "payment.cancelled":
        transaction.status = "CANCELLED"
    elif new_status:
        transaction.status = new_status

    db.commit()

    return {"status": "success", "message": "Webhook processed"}


@router.get("/subscription")
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's subscription status.

    **Returns**:
    - Current plan
    - Expiration date
    - Status
    """
    plan_id = current_user.subscription_plan or "free"
    plan = next((p for p in PLANS if p.id == plan_id), PLANS[0])

    return {
        "user_id": current_user.id,
        "plan": plan.id,
        "plan_name": plan.name,
        "status": current_user.subscription_status or "active",
        "expires_at": (
            current_user.subscription_expires_at.isoformat()
            if current_user.subscription_expires_at else None
        ),
        "can_upgrade": plan.id != "school",
    }


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel user's subscription.

    **Note**: Access continues until end of billing period
    (subscription_expires_at), matching HPG's collection-based billing
    (there is no recurring subscription to disable on HPG's side).
    """
    current_user.subscription_status = "cancelled"
    db.commit()

    return {
        "message": "Subscription cancelled",
        "access_until": (
            current_user.subscription_expires_at.isoformat()
            if current_user.subscription_expires_at else None
        ),
    }


@router.get("/transactions")
async def get_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's payment transaction history.

    **Returns**: List of past payments with status
    """
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(Transaction.created_at.desc()).all()

    return {
        "user_id": current_user.id,
        "transactions": [
            {
                "client_reference": t.client_reference,
                "transaction_id": t.transaction_id,
                "plan_id": t.plan_id,
                "amount": t.amount,
                "currency": t.currency,
                "provider": t.provider,
                "status": t.status,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            }
            for t in transactions
        ]
    }
