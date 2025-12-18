"""Asset model for media management."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.enums import AssetType


class Asset(Base):
    """
    Centralized asset management for all media files.
    
    Used for:
    - Question diagrams
    - Flashcard images
    - Teacher materials (PDFs, books, images)
    - Profile pictures
    - Achievement badges
    """
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    
    # File info
    filename = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    asset_type = Column(SQLEnum(AssetType), nullable=False)  # "image", "pdf", "video", "audio", "document"
    mime_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=True)  # In bytes
    
    # AI Metadata
    # This stores descriptions, OCR text, or tags that the AI can use
    # Example: {"description": "Diagram of a human heart", "tags": ["biology", "circulatory system"]}
    ai_metadata = Column(JSON, nullable=True)
    
    # Ownership
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    uploader = relationship("User")
    
    # Back-references for easy lookup
    questions = relationship("Question", back_populates="asset")
    flashcards = relationship("Flashcard", back_populates="asset")
    classroom_materials = relationship("ClassroomMaterial", back_populates="asset_ref")

    def __repr__(self):
        return f"<Asset {self.filename} ({self.asset_type})>"
