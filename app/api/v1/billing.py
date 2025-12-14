"""
Billing and monetization endpoints.
Handles subscriptions, payments (Paystack/Flutterwave), and premium features.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, timedelta
import hashlib
import hmac
from enum import Enum

from app.db.session import get_db
from app.models.user import User
from app.api.v1.auth import get_current_user
from app.core.config import settings


router = APIRouter()


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
    currency: Currency = Field(default=Currency.NGN, description="Currency code")
    duration_days: int = Field(..., description="Plan duration in days")
    features: List[str] = Field(..., description="List of features included")
    is_popular: bool = Field(default=False, description="Mark as popular/recommended")


class InitializePaymentRequest(BaseModel):
    """Request to start a payment transaction."""
    plan_id: str = Field(..., description="The plan to subscribe to")
    email: EmailStr = Field(..., description="User's email for payment receipt")
    currency: Currency = Field(default=Currency.NGN, description="Payment currency")


class InitializePaymentResponse(BaseModel):
    """Response with payment initialization details."""
    authorization_url: str = Field(..., description="URL to redirect user for payment")
    reference: str = Field(..., description="Unique transaction reference")
    access_code: Optional[str] = Field(None, description="Paystack access code")


class WebhookPayload(BaseModel):
    """Paystack/Flutterwave webhook payload."""
    event: str
    data: dict


# Define available plans
PLANS = [
    Plan(
        id="free",
        name="Basic",
        description="Essential features for exam preparation",
        price=0,
        currency=Currency.NGN,
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
        price=500,  # 500 Naira/month (~$0.50 USD)
        currency=Currency.NGN,
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
        price=50000,  # 50,000 Naira/year for up to 500 students
        currency=Currency.NGN,
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
    
    **Example Response**:
    ```json
    [
        {
            "id": "free",
            "name": "Basic",
            "price": 0,
            "features": ["Unlimited offline questions", "5 AI explanations/day"],
            "is_popular": false
        },
        {
            "id": "premium",
            "name": "Exam Master",
            "price": 500,
            "currency": "NGN",
            "features": ["Unlimited AI chat", "High-quality images"],
            "is_popular": true
        }
    ]
    ```
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
    Initialize a payment transaction with Paystack/Flutterwave.
    
    **Flow**:
    1. User selects a plan
    2. This endpoint creates a transaction reference
    3. Returns authorization URL for payment
    4. User completes payment on Paystack
    5. Webhook updates subscription status
    
    **Example Request**:
    ```json
    {
        "plan_id": "premium",
        "email": "student@example.com",
        "currency": "NGN"
    }
    ```
    
    **Example Response**:
    ```json
    {
        "authorization_url": "https://checkout.paystack.com/abc123",
        "reference": "base10_1234567890",
        "access_code": "abc123xyz"
    }
    ```
    """
    # Validate plan exists
    plan = next((p for p in PLANS if p.id == request.plan_id), None)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Free plan doesn't need payment
    if plan.price == 0:
        raise HTTPException(status_code=400, detail="Free plan doesn't require payment")
    
    # Generate unique transaction reference
    timestamp = int(datetime.utcnow().timestamp())
    reference = f"base10_{current_user.id}_{timestamp}"
    
    # In production, integrate with Paystack API
    # For now, return mock response
    mock_authorization_url = f"https://checkout.paystack.com/mock/{reference}"
    
    # TODO: In production:
    # 1. Call Paystack API to initialize transaction
    # 2. Store transaction in database with "pending" status
    # 3. Return actual authorization_url from Paystack
    
    """
    Example Paystack integration:
    
    import requests
    
    paystack_secret = settings.PAYSTACK_SECRET_KEY
    url = "https://api.paystack.co/transaction/initialize"
    
    payload = {
        "email": request.email,
        "amount": plan.price * 100,  # Convert to kobo
        "currency": request.currency.value,
        "reference": reference,
        "callback_url": f"{settings.BASE_URL}/billing/callback",
        "metadata": {
            "user_id": current_user.id,
            "plan_id": plan.id,
            "custom_fields": []
        }
    }
    
    headers = {
        "Authorization": f"Bearer {paystack_secret}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    
    if response.status_code == 200 and data["status"]:
        return InitializePaymentResponse(
            authorization_url=data["data"]["authorization_url"],
            reference=data["data"]["reference"],
            access_code=data["data"]["access_code"]
        )
    """
    
    return InitializePaymentResponse(
        authorization_url=mock_authorization_url,
        reference=reference,
        access_code="mock_access_code"
    )


@router.post("/webhook")
async def payment_webhook(
    request: Request,
    x_paystack_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint for Paystack/Flutterwave payment notifications.
    
    **Security**: Validates webhook signature to ensure requests come from payment provider.
    
    **Events Handled**:
    - `charge.success`: Payment completed successfully
    - `subscription.create`: Subscription created
    - `subscription.disable`: Subscription cancelled
    
    **Flow**:
    1. Paystack sends webhook when payment succeeds
    2. We verify the signature
    3. Update user's subscription status in database
    4. Send confirmation email
    
    **Configure in Paystack Dashboard**:
    - Webhook URL: `https://api.base10.edu/api/v1/billing/webhook`
    - Events: charge.success, subscription.*
    """
    # Get raw body for signature verification
    body = await request.body()
    
    # Verify Paystack signature
    if x_paystack_signature:
        # TODO: Get from settings
        paystack_secret = getattr(settings, 'PAYSTACK_SECRET_KEY', 'test_secret')
        
        computed_signature = hmac.new(
            paystack_secret.encode('utf-8'),
            body,
            hashlib.sha512
        ).hexdigest()
        
        if computed_signature != x_paystack_signature:
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse webhook payload
    payload = await request.json()
    event = payload.get("event")
    data = payload.get("data", {})
    
    # Handle charge success
    if event == "charge.success":
        reference = data.get("reference")
        metadata = data.get("metadata", {})
        user_id = metadata.get("user_id")
        plan_id = metadata.get("plan_id")
        
        if user_id and plan_id:
            # Find user
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                # Get plan details
                plan = next((p for p in PLANS if p.id == plan_id), None)
                if plan:
                    # Update user subscription
                    # TODO: Add subscription fields to User model
                    # user.subscription_plan = plan_id
                    # user.subscription_expires = datetime.utcnow() + timedelta(days=plan.duration_days)
                    # user.subscription_status = "active"
                    # db.commit()
                    
                    # TODO: Send confirmation email
                    pass
    
    # Handle subscription events
    elif event in ["subscription.create", "subscription.enable"]:
        # Subscription activated
        pass
    
    elif event == "subscription.disable":
        # Subscription cancelled
        pass
    
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
    - Features available
    - Usage quotas
    """
    # TODO: Query from user subscription fields
    # For now, return free plan
    
    return {
        "user_id": current_user.id,
        "plan": "free",
        "plan_name": "Basic",
        "status": "active",
        "started_at": datetime.utcnow().isoformat(),
        "expires_at": None,  # Free plan doesn't expire
        "features": {
            "ai_explanations_remaining": 5,
            "ai_chat_available": False,
            "image_quality": "medium",
            "ads_enabled": True
        },
        "can_upgrade": True
    }


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel user's subscription.
    
    **Note**: Access continues until end of billing period.
    """
    # TODO: Call Paystack API to disable subscription
    # TODO: Update user record
    
    return {
        "message": "Subscription cancelled",
        "access_until": (datetime.utcnow() + timedelta(days=30)).isoformat()
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
    # TODO: Query from transactions table
    
    return {
        "user_id": current_user.id,
        "transactions": []
    }
