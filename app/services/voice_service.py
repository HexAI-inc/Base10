"""
Voice Service for Speech-to-Text and Text-to-Speech.
Uses Gemini for high-accuracy transcription and Google TTS for natural voice output.
"""
import os
import logging
import google.generativeai as genai
from typing import Optional, BinaryIO
from app.core.config import settings

logger = logging.getLogger(__name__)

class VoiceService:
    """
    Handles voice interactions:
    1. STT (Speech-to-Text) using Gemini Multimodal
    2. TTS (Text-to-Speech) using high-quality providers
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'GOOGLE_API_KEY', '') or getattr(settings, 'GEMINI_API_KEY', '')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
            logger.warning("⚠️ Gemini API key not found. Voice STT will be disabled.")

    async def transcribe_audio(self, audio_file: BinaryIO, mime_type: str = "audio/wav") -> Optional[str]:
        """
        Transcribe audio using Gemini 1.5 Flash.
        Better than browser STT because it handles accents and background noise better.
        """
        if not self.model:
            return None
            
        try:
            # Read audio data
            audio_data = audio_file.read()
            
            # Prepare prompt for transcription
            prompt = "Transcribe this audio accurately. If it's a question about WAEC subjects (Math, English, Science), ensure technical terms are spelled correctly."
            
            response = self.model.generate_content([
                prompt,
                {
                    "mime_type": mime_type,
                    "data": audio_data
                }
            ])
            
            return response.text.strip()
        except Exception as e:
            logger.error(f"❌ Transcription failed: {e}")
            return None

    def text_to_speech_url(self, text: str, lang: str = 'en') -> str:
        """
        Generate a URL for Text-to-Speech.
        In a real app, this might return a pre-signed S3 URL or a streaming endpoint.
        For now, we'll provide a placeholder for high-quality TTS integration.
        """
        # Placeholder for integration with Google Cloud TTS or ElevenLabs
        # For now, we can use a public TTS proxy or return the text for client-side TTS
        return f"https://translate.google.com/translate_tts?ie=UTF-8&q={text}&tl={lang}&client=tw-ob"

voice_service = VoiceService()
