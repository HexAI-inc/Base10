"""Authentication API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.security import verify_password, get_password_hash, create_access_token, decode_token
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.schemas import UserCreate, UserLogin, UserResponse, Token
from app.services.onboarding_service import OnboardingService

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Dependency to get current authenticated user.
    Use in routes: current_user = Depends(get_current_user)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Register new user (email or phone).
    
    Critical for rural students: 
    - Supports phone-only registration (no email required)
    - Creates 7-day token for offline usage
    - Sends welcome email with verification link (if email provided)
    """
    # Check if user already exists
    if user_data.email:
        existing = db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    if user_data.phone_number:
        existing = db.query(User).filter(User.phone_number == user_data.phone_number).first()
        if existing:
            raise HTTPException(status_code=400, detail="Phone number already registered")
    
    # Create user
    new_user = User(
        email=user_data.email,
        phone_number=user_data.phone_number,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role or "student",
        is_active=True,
        is_verified=False  # Will be verified via email/SMS
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Send welcome email in background (non-blocking)
    if new_user.email:
        onboarding_service = OnboardingService(db)
        background_tasks.add_task(onboarding_service.send_welcome_email, new_user)
    
    # Create access token (7 days for offline-first)
    access_token = create_access_token(
        data={"sub": str(new_user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(new_user)
    )


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login with phone or email.
    
    OAuth2 compatible (username field accepts phone or email).
    Returns 7-day token for offline usage.
    """
    # Try to find user by email or phone
    user = db.query(User).filter(
        (User.email == form_data.username) | (User.phone_number == form_data.username)
    ).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is inactive")
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


@router.post("/login/json", response_model=Token)
def login_json(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login with phone or email using JSON payload.
    
    Alternative to OAuth2 form login for modern clients.
    Returns 7-day token for offline usage.
    """
    # Try to find user by email or phone
    user = db.query(User).filter(
        (User.email == login_data.identifier) | (User.phone_number == login_data.identifier)
    ).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is inactive")
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user


@router.get("/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Verify user email with token from email link.
    
    Query params:
    - token: Verification token from email
    
    Returns success message and redirects user to dashboard.
    """
    onboarding_service = OnboardingService(db)
    user = await onboarding_service.verify_email(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    return {
        "message": "Email verified successfully! Welcome to Base10.",
        "user_id": user.id,
        "verified_at": user.verified_at
    }


@router.post("/resend-verification")
async def resend_verification_email(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Resend verification email to current user.
    
    Requires authentication.
    """
    if current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    if not current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No email address associated with account"
        )
    
    onboarding_service = OnboardingService(db)
    success = await onboarding_service.send_verification_reminder(current_user)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email"
        )
    
    return {"message": "Verification email sent successfully"}


@router.post("/verify-sms")
def verify_sms_code(phone: str, code: str, db: Session = Depends(get_db)):
    """
    SMS verification (Phase 3).
    TODO: Integrate with Twilio or Africa's Talking
    """
    # Placeholder for SMS verification logic
    user = db.query(User).filter(User.phone_number == phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # TODO: Verify code from Redis/SMS service
    user.is_verified = True
    db.commit()
    
    return {"status": "verified", "message": "Phone number verified successfully"}
