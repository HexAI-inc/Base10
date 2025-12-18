"""Admin Content Moderation API."""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from app.db.session import get_db
from app.models.user import User
from app.models.question import Question
from app.models.enums import Subject, DifficultyLevel, Topic
from app.models.flashcard import FlashcardDeck, Flashcard
from app.models.asset import Asset
from app.schemas import schemas
from app.api.v1.admin import get_admin_user
from app.services.storage import StorageService, AssetType

router = APIRouter()

# ============= Question Moderation =============

@router.post("/questions", response_model=schemas.QuestionResponse)
async def create_question(
    data: schemas.QuestionCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Create a new static question (Admin only)."""
    new_question = Question(**data.dict())
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return new_question

@router.get("/questions", response_model=List[schemas.QuestionResponse])
async def list_questions(
    subject: Optional[Subject] = None,
    topic: Optional[Topic] = None,
    difficulty: Optional[DifficultyLevel] = None,
    search: Optional[str] = Query(None, description="Search in question content"),
    limit: int = Query(50, le=100),
    skip: int = 0,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """List and search questions for moderation (Admin only)."""
    query = db.query(Question).filter(Question.deleted_at == None)
    
    if subject:
        query = query.filter(Question.subject == subject)
    if topic:
        query = query.filter(Question.topic == topic)
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)
    if search:
        query = query.filter(Question.content.ilike(f"%{search}%"))
        
    return query.order_by(Question.created_at.desc()).offset(skip).limit(limit).all()

@router.put("/questions/{question_id}", response_model=schemas.QuestionResponse)
async def update_question(
    question_id: int,
    data: schemas.QuestionCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Update an existing question (Admin only)."""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    for key, value in data.dict().items():
        setattr(question, key, value)
    
    db.commit()
    db.refresh(question)
    return question

@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Soft delete a question (Admin only)."""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    question.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Question deleted successfully"}

# ============= Asset Moderation =============

@router.post("/assets/upload", response_model=schemas.AssetResponse)
async def upload_asset(
    file: UploadFile = File(...),
    asset_type: str = Query(..., description="image, pdf, etc."),
    ai_description: Optional[str] = Query(None, description="Description for AI context"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Upload a new asset and store metadata (Admin only)."""
    storage_service = StorageService()
    
    # Determine AssetType enum
    try:
        a_type = AssetType(asset_type)
    except ValueError:
        a_type = AssetType.QUESTION_DIAGRAM # Default
        
    # Upload to storage
    url = storage_service.upload_image(
        file.file,
        a_type,
        file.filename,
        user_id=admin.id
    )
    
    # Create asset record
    new_asset = Asset(
        filename=file.filename,
        url=url,
        asset_type=asset_type,
        mime_type=file.content_type,
        ai_metadata={"description": ai_description} if ai_description else {},
        uploaded_by_id=admin.id
    )
    
    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)
    return new_asset

@router.get("/assets", response_model=List[schemas.AssetResponse])
async def list_assets(
    asset_type: Optional[str] = None,
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """List all assets with metadata (Admin only)."""
    query = db.query(Asset)
    if asset_type:
        query = query.filter(Asset.asset_type == asset_type)
    
    return query.limit(limit).all()

@router.put("/assets/{asset_id}/metadata")
async def update_asset_metadata(
    asset_id: int,
    metadata: Dict[str, Any],
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Update AI metadata for an asset (Admin only)."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    asset.ai_metadata = metadata
    db.commit()
    return {"message": "Metadata updated", "asset_id": asset_id}

# ============= Flashcard Moderation =============

@router.get("/flashcards/decks", response_model=List[schemas.FlashcardDeckResponse])
async def list_decks(
    subject: Optional[Subject] = None,
    difficulty: Optional[DifficultyLevel] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """List all flashcard decks (Admin only)."""
    query = db.query(FlashcardDeck)
    if subject:
        query = query.filter(FlashcardDeck.subject == subject)
    if difficulty:
        query = query.filter(FlashcardDeck.difficulty == difficulty)
    
    return query.all()

@router.post("/flashcards/decks", response_model=schemas.FlashcardDeckResponse)
async def create_deck(
    data: schemas.FlashcardDeckCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Create a new flashcard deck (Admin only)."""
    deck = FlashcardDeck(**data.dict())
    db.add(deck)
    db.commit()
    db.refresh(deck)
    return deck

@router.post("/flashcards", response_model=schemas.FlashcardResponse)
async def create_flashcard(
    data: schemas.FlashcardCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Create a new flashcard in a deck (Admin only)."""
    card = Flashcard(**data.dict())
    db.add(card)
    
    # Update deck card count
    deck = db.query(FlashcardDeck).filter(FlashcardDeck.id == data.deck_id).first()
    if deck:
        deck.card_count += 1
        
    db.commit()
    db.refresh(card)
    return card
