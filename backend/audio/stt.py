"""Speech-to-Text module with graceful fallback"""

import os
import io
import logging
from typing import Optional
from dotenv import load_dotenv

try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False
    print("speech_recognition not installed. Install with: pip install SpeechRecognition")

try:
    from openai import OpenAI, AsyncOpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

load_dotenv()

logger = logging.getLogger(__name__)


class SpeechToText:
    """Converts speech audio to text using available providers"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        language: str = "en"
    ):
        """
        Initialize Speech-to-Text converter
        
        Args:
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
            language: Language code (default: "en" for English)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.language = language
        self.is_available = False
        self.provider = None
        self.recognizer = None
        self.client = None
        self.async_client = None
        
        # Try Google Speech Recognition first (free, no API key needed)
        if HAS_SR:
            try:
                self.recognizer = sr.Recognizer()
                self.is_available = True
                self.provider = "google"
                logger.info("✅ STT initialized with provider: Google Speech Recognition (free)")
                return
            except Exception as e:
                logger.warning(f"⚠️  Google Speech Recognition failed: {e}")
        
        # Try OpenAI Whisper as fallback (requires API key)
        if HAS_OPENAI and self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
                self.async_client = AsyncOpenAI(api_key=self.api_key)
                self.is_available = True
                self.provider = "openai"
                logger.info("✅ STT initialized with provider: OpenAI Whisper")
                return
            except Exception as e:
                logger.warning(f"⚠️  OpenAI Whisper failed: {e}")
        
        # If we reach here, STT is not available
        logger.warning(
            "⚠️  STT not available!\n"
            "Option 1: Install speech_recognition\n"
            "  pip install SpeechRecognition pydub\n"
            "Option 2: Set OPENAI_API_KEY for OpenAI Whisper\n"
            "Voice input will still work, but transcription will be disabled."
        )
        self.is_available = False
    
    async def transcribe(self, audio_data: bytes) -> str:
        """
        Transcribe audio data to text
        
        Args:
            audio_data: Raw audio bytes (WAV format)
        
        Returns:
            Transcribed text, or empty string if transcription unavailable
        """
        if not self.is_available:
            logger.debug("STT not available - returning empty string")
            return ""
        
        try:
            if self.provider == "google":
                return await self._transcribe_google(audio_data)
            elif self.provider == "openai":
                return await self._transcribe_openai(audio_data)
        except Exception as e:
            logger.error(f"Transcription error: {e}")
        
        return ""
    
    async def _transcribe_google(self, audio_data: bytes) -> str:
        """
        Transcribe using Google Speech Recognition (free)
        
        Args:
            audio_data: Audio bytes
        
        Returns:
            Transcribed text
        """
        try:
            # Convert bytes to AudioData (16kHz, 16-bit mono)
            audio = sr.AudioData(audio_data, 16000, 2)
            
            # Google Speech Recognition (free, no API key needed)
            text = self.recognizer.recognize_google(audio, language=self.language)
            logger.debug(f"Google STT: {text}")
            return text.strip()
        
        except sr.UnknownValueError:
            logger.debug("Could not understand audio (silence or too quiet)")
            return ""
        
        except sr.RequestError as e:
            logger.warning(f"Google STT request failed: {e}")
            return ""
        
        except Exception as e:
            logger.error(f"Google STT error: {e}")
            return ""
    
    async def _transcribe_openai(self, audio_data: bytes) -> str:
        """
        Transcribe using OpenAI Whisper (requires API key)
        
        Args:
            audio_data: Audio bytes
        
        Returns:
            Transcribed text
        """
        try:
            # Create file-like object
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"
            
            # Transcribe using OpenAI Whisper
            transcript = await self.async_client.audio.transcriptions.create(
                model="whisper-1",
                file=("audio.wav", audio_file, "audio/wav"),
                language=self.language
            )
            
            text = transcript.text.strip()
            logger.debug(f"OpenAI Whisper: {text}")
            return text
        
        except Exception as e:
            logger.error(f"OpenAI Whisper error: {e}")
            return ""
    
    def transcribe_sync(self, audio_data: bytes) -> str:
        """
        Synchronous transcription (blocking)
        
        Args:
            audio_data: Raw audio bytes (WAV format)
        
        Returns:
            Transcribed text
        """
        if not self.is_available:
            logger.debug("STT not available")
            return ""
        
        try:
            if self.provider == "google":
                # Convert bytes to AudioData
                audio = sr.AudioData(audio_data, 16000, 2)
                text = self.recognizer.recognize_google(audio, language=self.language)
                logger.debug(f"Google STT (sync): {text}")
                return text.strip()
            
            elif self.provider == "openai":
                # OpenAI Whisper synchronous
                audio_file = io.BytesIO(audio_data)
                audio_file.name = "audio.wav"
                
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=("audio.wav", audio_file, "audio/wav"),
                    language=self.language
                )
                
                text = transcript.text.strip()
                logger.debug(f"OpenAI Whisper (sync): {text}")
                return text
        
        except Exception as e:
            logger.error(f"Sync transcription error: {e}")
        
        return ""
