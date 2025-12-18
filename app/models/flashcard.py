"""Flashcard model for spaced repetition learning."""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, func, Index, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.enums import Subject, DifficultyLevel


class FlashcardDeck(Base):
    """
    Collection of flashcards grouped by topic.
    
    Examples:
    - "Physics Definitions"
    - "Chemistry Formulas"
    - "Biology Terminology"
    """
    __tablename__ = "flashcard_decks"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Deck info
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    subject = Column(SQLEnum(Subject), nullable=False, index=True)
    difficulty = Column(SQLEnum(DifficultyLevel), nullable=False)  # easy, medium, hard
    
    # Content
    card_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    cards = relationship("Flashcard", back_populates="deck")
    
    def __repr__(self):
        return f"<Deck {self.name}: {self.card_count} cards>"


class Flashcard(Base):
    """
    Individual flashcard (front + back).
    
    Design:
    - front: The question/prompt
    - back: The answer
    - Supports images (stored separately)
    """
    __tablename__ = "flashcards"
    
    id = Column(Integer, primary_key=True, index=True)
    deck_id = Column(Integer, ForeignKey("flashcard_decks.id"), nullable=False, index=True)
    
    # Card content
    front = Column(Text, nullable=False)  # Question/Prompt
    back = Column(Text, nullable=False)   # Answer
    image_url = Column(String(500), nullable=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    deck = relationship("FlashcardDeck", back_populates="cards")
    reviews = relationship("FlashcardReview", back_populates="card")
    asset = relationship("Asset", back_populates="flashcards")
    
    def __repr__(self):
        return f"<Card {self.id}: {self.front[:30]}...>"


class FlashcardReview(Base):
    """
    User's progress on individual flashcards (SuperMemo algorithm).
    
    Design:
    - ease_factor: How easy the card is (1.3 = hard, 2.5 = normal, 3.0+ = easy)
    - interval: Days until next review
    - repetitions: Consecutive correct answers
    """
    __tablename__ = "flashcard_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    card_id = Column(Integer, ForeignKey("flashcards.id"), nullable=False, index=True)
    
    # SuperMemo 2 algorithm fields
    ease_factor = Column(Float, default=2.5)  # 1.3 to 3.0+
    interval = Column(Integer, default=1)     # Days until next review
    repetitions = Column(Integer, default=0)  # Consecutive correct answers
    
    # Review tracking
    last_reviewed_at = Column(DateTime(timezone=True), nullable=True)
    next_review_date = Column(DateTime(timezone=True), nullable=True)
    
    # Offline sync
    synced_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="flashcard_progress")
    card = relationship("Flashcard", back_populates="reviews")
    
    # Index for "due today" queries
    __table_args__ = (
        Index('idx_flashcard_next_review', 'user_id', 'next_review_date'),
        Index('idx_flashcard_review_updated', 'updated_at'),
    )
    
    def __repr__(self):
        return f"<Review U{self.user_id} C{self.card_id}: EF={self.ease_factor:.1f} Interval={self.interval}d>"
