"""Voice API endpoints for STT and TTS."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from typing import Dict, Any
import logging

from app.services.voice_service import voice_service
from app.services.ai_service import (
    generate_explanation, 
    check_ai_quota, 
    increment_ai_usage
)
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/transcribe", status_code=status.HTTP_200_OK)
async def transcribe_audio(
    audio: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Transcribe uploaded audio file to text.
    Supports wav, mp3, m4a, etc.
    """
    # Check Quota
    if not check_ai_quota(db, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI quota exceeded. Please wait for reset or upgrade."
        )

    if not audio.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an audio recording"
        )
        
    text = await voice_service.transcribe_audio(audio.file, audio.content_type)
    
    if not text:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to transcribe audio"
        )
        
    # Increment usage
    increment_ai_usage(db, current_user.id, "voice_stt")
        
    return {"text": text}

@router.post("/tts", status_code=status.HTTP_200_OK)
async def text_to_speech(
    text: str,
    current_user: User = Depends(get_current_user)
):
    """
    Convert text to high-quality speech URL.
    """
    audio_url = voice_service.text_to_speech_url(text)
    return {"audio_url": audio_url}

@router.post("/voice-chat", status_code=status.HTTP_200_OK)
async def voice_chat(
    audio: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Full Voice-to-Voice loop:
    1. Transcribe student's voice
    2. Get AI response (Socratic)
    3. Return both text and audio URL
    """
    # Check Quota
    if not check_ai_quota(db, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI quota exceeded. Please wait for reset or upgrade."
        )

    # 1. Transcribe
    transcript = await voice_service.transcribe_audio(audio.file, audio.content_type)
    if not transcript:
        raise HTTPException(status_code=500, detail="Could not hear you clearly")
        
    # 2. Get AI Response (Using existing AI service)
    # For simplicity, we'll use a generic chat response here
    # In a real scenario, we'd pass this to the Socratic tutor
    from app.services.ai_service import model as ai_model
    
    prompt = f"The student said: '{transcript}'. Respond as a helpful WAEC tutor in 1-2 sentences."
    response = ai_model.generate_content(prompt)
    ai_text = response.text.strip()
    
    # 3. Generate TTS
    audio_url = voice_service.text_to_speech_url(ai_text)
    
    # Increment usage
    increment_ai_usage(db, current_user.id, "voice_chat")
    
    return {
        "user_text": transcript,
        "ai_text": ai_text,
        "audio_url": audio_url
    }
