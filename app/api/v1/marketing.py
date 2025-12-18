"""Marketing and Waitlist API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

from app.db.session import get_db
from app.models.user import User
from app.models.marketing import WaitlistLead
from app.schemas import schemas
from app.api.v1.auth import get_current_user
from app.api.v1.admin import get_admin_user

router = APIRouter()

@router.post("/waitlist", status_code=status.HTTP_201_CREATED)
async def join_waitlist(
    lead: schemas.WaitlistCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Join the Base10 waitlist.
    
    - Sanitizes phone number
    - Deduplicates by phone number
    - Saves lead to database
    - Triggers welcome SMS (optional)
    """
    # 1. Basic sanitization (remove spaces, ensure +)
    phone = lead.phone_number.replace(" ", "").replace("-", "")
    if not phone.startswith("+"):
        # Default to Gambia if no country code (for local testing)
        if len(phone) == 7:
            phone = "+220" + phone
    
    # 2. Check for duplicate
    existing = db.query(WaitlistLead).filter(WaitlistLead.phone_number == phone).first()
    if existing:
        # Return 200 OK instead of error to be idempotent and not leak info
        return {"message": "You are already on the list! We will notify you soon.", "status": "already_joined"}

    # 3. Create lead
    new_lead = WaitlistLead(
        full_name=lead.full_name,
        phone_number=phone,
        email=lead.email,
        school_name=lead.school_name,
        education_level=lead.education_level,
        location=lead.location,
        device_type=lead.device_type,
        referral_source=lead.referral_source
    )
    
    try:
        db.add(new_lead)
        db.commit()
        db.refresh(new_lead)
        
        # 4. Trigger Welcome SMS (Async)
        # background_tasks.add_task(send_welcome_sms, phone, lead.full_name)
        
        return {"message": "Successfully joined the waitlist!", "status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to join waitlist: {str(e)}"
        )

@router.get("/leads", response_model=List[schemas.WaitlistLeadResponse])
async def get_waitlist_leads(
    skip: int = 0,
    limit: int = 100,
    location: Optional[str] = None,
    device: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Get all waitlist leads (Admin only)."""
    query = db.query(WaitlistLead)
    
    if location:
        query = query.filter(WaitlistLead.location.ilike(f"%{location}%"))
    if device:
        query = query.filter(WaitlistLead.device_type == device)
        
    return query.order_by(WaitlistLead.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/stats", response_model=schemas.MarketingStats)
async def get_marketing_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Get marketing analytics and waitlist breakdown (Admin only)."""
    total_leads = db.query(WaitlistLead).count()
    if total_leads == 0:
        return {
            "total_leads": 0,
            "device_breakdown": {},
            "top_schools": [],
            "conversion_rate": 0.0
        }
    
    # Device breakdown
    device_stats = db.query(
        WaitlistLead.device_type,
        func.count(WaitlistLead.id)
    ).group_by(WaitlistLead.device_type).all()
    
    device_breakdown = {
        str(device or "Unknown"): f"{(count / total_leads) * 100:.1f}%"
        for device, count in device_stats
    }
    
    # Top schools
    school_stats = db.query(
        WaitlistLead.school_name,
        func.count(WaitlistLead.id).label('count')
    ).filter(WaitlistLead.school_name.isnot(None)).group_by(
        WaitlistLead.school_name
    ).order_by(func.count(WaitlistLead.id).desc()).limit(5).all()
    
    top_schools = [{"name": s[0], "count": s[1]} for s in school_stats]
    
    # Conversion rate
    converted_count = db.query(WaitlistLead).filter(WaitlistLead.is_converted == True).count()
    conversion_rate = (converted_count / total_leads) * 100
    
    return {
        "total_leads": total_leads,
        "device_breakdown": device_breakdown,
        "top_schools": top_schools,
        "conversion_rate": round(conversion_rate, 2)
    }

@router.post("/broadcast")
async def broadcast_sms(
    request: schemas.BroadcastRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Send broadcast SMS to waitlist leads (Admin only).
    
    In production, this would integrate with a service like Twilio or Africa's Talking.
    """
    query = db.query(WaitlistLead.phone_number)
    
    if request.filter_location:
        query = query.filter(WaitlistLead.location.ilike(f"%{request.filter_location}%"))
    if request.filter_device:
        query = query.filter(WaitlistLead.device_type == request.filter_device)
        
    leads = query.all()
    phone_numbers = [l[0] for l in leads]
    
    if not phone_numbers:
        return {"message": "No leads found matching filters", "count": 0}
    
    # background_tasks.add_task(send_bulk_sms, phone_numbers, request.message)
    
    return {
        "message": f"Broadcast queued for {len(phone_numbers)} leads",
        "count": len(phone_numbers),
        "sample_message": request.message
    }
