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

router = APIRouter()


# Response schemas
class CardSchema(BaseModel):
    """Individual flashcard."""
    id: int
    front: str
    back: str
    image_url: Optional[str]
    
    class Config:
        from_attributes = True


class DeckSchema(BaseModel):
    """Flashcard deck with cards."""
    id: int
    name: str
    description: Optional[str]
    subject: str
    difficulty: str
    card_count: int
    cards: List[CardSchema]
    
    class Config:
        from_attributes = True


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


@router.get("/decks", response_model=List[DeckSchema])
async def get_flashcard_decks(
    subject: Optional[str] = None,
    difficulty: Optional[str] = None,
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
            Flashcard.deleted_at == None
        ).all()
        
        result.append(DeckSchema(
            id=deck.id,
            name=deck.name,
            description=deck.description,
            subject=deck.subject,
            difficulty=deck.difficulty,
            card_count=len(cards),
            cards=[CardSchema.from_orm(c) for c in cards]
        ))
    
    return result


@router.get("/due", response_model=List[CardSchema])
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
    
    return [CardSchema.from_orm(c) for c in cards]


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
