"""Flashcard endpoints for spaced repetition learning."""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.db.session import get_db
from app.models.user import User
from app.models.flashcard import FlashcardDeck, Flashcard, FlashcardReview
from app.core.security import get_current_user
from app.models.enums import Subject, DifficultyLevel, UserRole

from app.schemas.schemas import AssetResponse, FlashcardResponse, FlashcardDeckResponse

router = APIRouter()


# Request schemas
class CreateDeckRequest(BaseModel):
    """Request to create a new flashcard deck."""
    name: str
    description: Optional[str] = None
    subject: Subject
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM


class CreateFlashcardRequest(BaseModel):
    """Request to create a new flashcard."""
    deck_id: int
    front: str
    back: str
    asset_id: Optional[int] = None


class GenerateFlashcardsRequest(BaseModel):
    """Request to generate flashcards using AI."""
    subject: Subject
    topic: str
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    count: int = Query(10, ge=5, le=20, description="Number of flashcards to generate")


class ApproveFlashcardRequest(BaseModel):
    """Request to approve AI-generated flashcards."""
    flashcard_ids: List[int]
    approved: bool = True
    moderator_notes: Optional[str] = None


# Response schemas
class ReviewSchema(BaseModel):
    """User's review progress on a card."""
    card_id: int
    ease_factor: float
    interval: int
    repetitions: int
    next_review_date: Optional[datetime]


class FlashcardSyncRequest(BaseModel):
    """Sync flashcard review data from offline device."""
    card_id: int
    quality: int  # 0-5 (SuperMemo 2 algorithm)
    reviewed_at: datetime


@router.get("/decks", response_model=List[FlashcardDeckResponse])
async def get_flashcard_decks(
    subject: Optional[Subject] = None,
    difficulty: Optional[DifficultyLevel] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download flashcard decks for offline study.
    
    Lightweight JSON packs of facts (e.g., "Physics Definitions").
    Filtered by user's preferred subjects if set.
    
    Query params:
    - subject: Filter by subject (Mathematics, Physics, etc.)
    - difficulty: Filter by difficulty (easy, medium, hard)
    """
    query = db.query(FlashcardDeck)
    
    # Filter by subject
    if subject:
        query = query.filter(FlashcardDeck.subject == subject)
    elif current_user.preferred_subjects:
        # Filter by user's preferred subjects
        import json
        try:
            preferred = json.loads(current_user.preferred_subjects)
            query = query.filter(FlashcardDeck.subject.in_(preferred))
        except:
            pass
    
    # Filter by difficulty
    if difficulty:
        query = query.filter(FlashcardDeck.difficulty == difficulty)
    
    decks = query.all()
    
    # Load cards for each deck
    result = []
    for deck in decks:
        cards = db.query(Flashcard).filter(
            Flashcard.deck_id == deck.id,
            Flashcard.deleted_at == None,
            Flashcard.approved == True  # Only show approved cards
        ).all()
        
        result.append(FlashcardDeckResponse(
            id=deck.id,
            name=deck.name,
            description=deck.description,
            subject=deck.subject,
            difficulty=deck.difficulty,
            card_count=len(cards),
            cards=[FlashcardResponse.from_orm(c) for c in cards]
        ))
    
    return result


@router.get("/due", response_model=List[FlashcardResponse])
async def get_due_flashcards(
    limit: int = Query(20, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get flashcards due for review today.
    
    Uses SuperMemo 2 spaced repetition algorithm.
    Returns cards where next_review_date <= today.
    """
    today = datetime.utcnow()
    
    # Get cards due for review
    due_reviews = db.query(FlashcardReview).filter(
        FlashcardReview.user_id == current_user.id,
        FlashcardReview.next_review_date <= today
    ).limit(limit).all()
    
    # Load the actual cards
    card_ids = [r.card_id for r in due_reviews]
    cards = db.query(Flashcard).filter(Flashcard.id.in_(card_ids)).all()
    
    return [FlashcardResponse.from_orm(c) for c in cards]


@router.post("/sync", status_code=200)
async def sync_flashcard_progress(
    syncs: List[FlashcardSyncRequest],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sync flashcard review data from offline device.
    
    SuperMemo 2 Algorithm:
    - quality: 0-5 (0=complete blackout, 5=perfect)
    - If quality >= 3: increase interval
    - If quality < 3: reset interval to 1 day
    
    Example:
        POST /api/v1/flashcards/sync
        [
            {
                "card_id": 42,
                "quality": 4,
                "reviewed_at": "2025-12-14T10:30:00Z"
            }
        ]
    """
    synced_count = 0
    
    for sync in syncs:
        # Get or create review record
        review = db.query(FlashcardReview).filter(
            FlashcardReview.user_id == current_user.id,
            FlashcardReview.card_id == sync.card_id
        ).first()
        
        if not review:
            # First time reviewing this card
            review = FlashcardReview(
                user_id=current_user.id,
                card_id=sync.card_id,
                ease_factor=2.5,
                interval=1,
                repetitions=0
            )
            db.add(review)
        
        # Apply SuperMemo 2 algorithm
        quality = sync.quality
        
        if quality >= 3:
            # Correct answer - increase interval
            if review.repetitions == 0:
                review.interval = 1
            elif review.repetitions == 1:
                review.interval = 6
            else:
                review.interval = int(review.interval * review.ease_factor)
            
            review.repetitions += 1
            
            # Adjust ease factor
            review.ease_factor = max(1.3, review.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
        
        else:
            # Incorrect answer - reset
            review.repetitions = 0
            review.interval = 1
        
        # Set next review date
        review.last_reviewed_at = sync.reviewed_at
        review.next_review_date = sync.reviewed_at + timedelta(days=review.interval)
        review.synced_at = datetime.utcnow()
        
        synced_count += 1
    
    db.commit()
    
    return {
        "message": f"Synced {synced_count} flashcard reviews",
        "synced_count": synced_count
    }


@router.get("/progress", response_model=List[ReviewSchema])
async def get_flashcard_progress(
    deck_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's flashcard review progress.
    
    Optionally filter by deck_id.
    """
    query = db.query(FlashcardReview).filter(
        FlashcardReview.user_id == current_user.id
    )
    
    if deck_id:
        # Join with Flashcard to filter by deck
        query = query.join(Flashcard).filter(Flashcard.deck_id == deck_id)
    
    reviews = query.all()
    
    return [
        ReviewSchema(
            card_id=r.card_id,
            ease_factor=r.ease_factor,
            interval=r.interval,
            repetitions=r.repetitions,
            next_review_date=r.next_review_date
        )
        for r in reviews
    ]


# ==================== CREATION ENDPOINTS ====================

@router.post("/decks", response_model=FlashcardDeckResponse)
async def create_flashcard_deck(
    request: CreateDeckRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new flashcard deck.
    
    Requires teacher or admin role.
    """
    # Check permissions - only teachers and admins can create decks
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers and admins can create flashcard decks"
        )
    
    # Create the deck
    deck = FlashcardDeck(
        name=request.name,
        description=request.description,
        subject=request.subject,
        difficulty=request.difficulty,
        card_count=0
    )
    
    db.add(deck)
    db.commit()
    db.refresh(deck)
    
    return FlashcardDeckResponse.from_orm(deck)


@router.post("/cards", response_model=FlashcardResponse)
async def create_flashcard(
    request: CreateFlashcardRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new flashcard in an existing deck.
    
    Requires teacher or admin role.
    """
    # Check permissions
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers and admins can create flashcards"
        )
    
    # Verify deck exists and user has access
    deck = db.query(FlashcardDeck).filter(FlashcardDeck.id == request.deck_id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Flashcard deck not found")
    
    # Create the flashcard
    card = Flashcard(
        deck_id=request.deck_id,
        front=request.front,
        back=request.back,
        asset_id=request.asset_id
    )
    
    db.add(card)
    db.commit()
    db.refresh(card)
    
    # Update deck card count
    deck.card_count = db.query(Flashcard).filter(
        Flashcard.deck_id == deck.id,
        Flashcard.deleted_at == None,
        Flashcard.approved == True
    ).count()
    db.commit()
    
    return FlashcardResponse.from_orm(card)


@router.post("/generate", response_model=List[FlashcardResponse])
async def generate_flashcards_ai(
    request: GenerateFlashcardsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate flashcards using AI for a specific topic.
    
    Creates flashcards on-the-fly using Gemini AI.
    Cards are stored temporarily and require moderator approval.
    """
    # Check AI quota
    from app.services.ai_service import check_ai_quota, increment_ai_usage
    if not check_ai_quota(db, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI quota exceeded. Please wait for reset or upgrade."
        )
    
    try:
        from app.services.ai_service import generate_flashcard_deck
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="AI flashcard generation service is currently unavailable."
        )
    
    try:
        # Generate flashcards using AI
        flashcards_data = await generate_flashcard_deck(
            subject=request.subject,
            topic=request.topic,
            difficulty=request.difficulty,
            count=request.count
        )
        
        # Create a temporary deck for these AI-generated cards
        temp_deck = FlashcardDeck(
            name=f"AI Generated: {request.topic}",
            description=f"AI-generated flashcards for {request.subject.value} - {request.topic}",
            subject=request.subject,
            difficulty=request.difficulty,
            card_count=0
        )
        db.add(temp_deck)
        db.commit()
        db.refresh(temp_deck)
        
        # Create flashcards
        created_cards = []
        for card_data in flashcards_data:
            card = Flashcard(
                deck_id=temp_deck.id,
                front=card_data["front"],
                back=card_data["back"]
            )
            db.add(card)
            created_cards.append(card)
        
        db.commit()
        
        # Update deck count
        temp_deck.card_count = len(created_cards)
        db.commit()
        
        # Increment usage
        increment_ai_usage(db, current_user.id, "flashcard_generation")
        
        return [FlashcardResponse.from_orm(card) for card in created_cards]
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate flashcards: {str(e)}"
        )


@router.post("/moderate", status_code=200)
async def moderate_flashcards(
    request: ApproveFlashcardRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve or reject AI-generated flashcards.
    
    Requires moderator or admin role.
    Approved cards are marked as approved and can be used.
    Rejected cards are soft-deleted.
    """
    # Check permissions - only moderators and admins can moderate
    if current_user.role not in [UserRole.MODERATOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only moderators and admins can moderate flashcards"
        )
    
    approved_count = 0
    rejected_count = 0
    
    for card_id in request.flashcard_ids:
        card = db.query(Flashcard).filter(Flashcard.id == card_id).first()
        if not card:
            continue
        
        if request.approved:
            # Mark as approved
            card.approved = True
            card.moderator_id = current_user.id
            card.approved_at = datetime.utcnow()
            approved_count += 1
        else:
            # Soft delete rejected cards
            card.deleted_at = datetime.utcnow()
            rejected_count += 1
    
    db.commit()
    
    # Update card counts for affected decks
    affected_deck_ids = set()
    for card_id in request.flashcard_ids:
        card = db.query(Flashcard).filter(Flashcard.id == card_id).first()
        if card:
            affected_deck_ids.add(card.deck_id)
    
    for deck_id in affected_deck_ids:
        deck = db.query(FlashcardDeck).filter(FlashcardDeck.id == deck_id).first()
        if deck:
            deck.card_count = db.query(Flashcard).filter(
                Flashcard.deck_id == deck.id,
                Flashcard.deleted_at == None,
                Flashcard.approved == True
            ).count()
    
    db.commit()
    
    return {
        "message": f"Moderated {len(request.flashcard_ids)} flashcards",
        "approved": approved_count,
        "rejected": rejected_count,
        "moderator_notes": request.moderator_notes
    }
