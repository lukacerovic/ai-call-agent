"""Text-to-Speech module using multiple providers"""

import os
import io
import logging
from typing import Optional
from enum import Enum
from dotenv import load_dotenv

try:
    from openai import OpenAI, AsyncOpenAI
except ImportError:
    print("OpenAI library not installed. Install with: pip install openai")

try:
    from gtts import gTTS
except ImportError:
    print("gTTS not installed. Install with: pip install gtts")

load_dotenv()

logger = logging.getLogger(__name__)


class TTSProvider(str, Enum):
    """Available TTS providers"""
    OPENAI = "openai"
    GTTS = "gtts"
    PYTTSX3 = "pyttsx3"


class TextToSpeech:
    """Converts text to speech audio"""
    
    def __init__(
        self,
        provider: str = "openai",
        voice: str = "alloy",
        language: str = "en",
        speed: float = 1.0
    ):
        """
        Initialize Text-to-Speech converter
        
        Args:
            provider: TTS provider ("openai", "gtts", or "pyttsx3")
            voice: Voice to use (depends on provider)
                - OpenAI: alloy, echo, fable, onyx, nova, shimmer
                - gTTS: only language setting
            language: Language code (e.g., "en" for English)
            speed: Speech speed (1.0 = normal)
        """
        self.provider = os.getenv("TTS_PROVIDER", provider).lower()
        self.voice = voice
        self.language = language
        self.speed = speed
        
        # Initialize provider-specific clients
        if self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
            self.client = OpenAI(api_key=api_key)
            self.async_client = AsyncOpenAI(api_key=api_key)
        
        logger.info(f"TTS initialized with provider: {self.provider}, voice: {self.voice}")
    
    async def synthesize(self, text: str) -> bytes:
        """
        Convert text to speech audio
        
        Args:
            text: Text to convert to speech
        
        Returns:
            Audio data as bytes (MP3 format)
        """
        try:
            if self.provider == "openai":
                return await self._synthesize_openai(text)
            elif self.provider == "gtts":
                return await self._synthesize_gtts(text)
            else:
                logger.warning(f"Unknown provider: {self.provider}, falling back to OpenAI")
                return await self._synthesize_openai(text)
        
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return b""
    
    def synthesize_sync(self, text: str) -> bytes:
        """
        Synchronous version of synthesize
        
        Args:
            text: Text to convert to speech
        
        Returns:
            Audio data as bytes (MP3 format)
        """
        try:
            if self.provider == "openai":
                return self._synthesize_openai_sync(text)
            elif self.provider == "gtts":
                return self._synthesize_gtts_sync(text)
            else:
                logger.warning(f"Unknown provider: {self.provider}, falling back to OpenAI")
                return self._synthesize_openai_sync(text)
        
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return b""
    
    async def _synthesize_openai(self, text: str) -> bytes:
        """
        Synthesize using OpenAI API (async)
        
        Args:
            text: Text to synthesize
        
        Returns:
            Audio bytes
        """
        response = await self.async_client.audio.speech.create(
            model="tts-1",
            voice=self.voice,
            input=text,
            speed=self.speed
        )
        
        return response.content
    
    def _synthesize_openai_sync(self, text: str) -> bytes:
        """
        Synthesize using OpenAI API (sync)
        
        Args:
            text: Text to synthesize
        
        Returns:
            Audio bytes
        """
        response = self.client.audio.speech.create(
            model="tts-1",
            voice=self.voice,
            input=text,
            speed=self.speed
        )
        
        return response.content
    
    async def _synthesize_gtts(self, text: str) -> bytes:
        """
        Synthesize using Google Text-to-Speech (async wrapper)
        
        Args:
            text: Text to synthesize
        
        Returns:
            Audio bytes
        """
        return self._synthesize_gtts_sync(text)
    
    def _synthesize_gtts_sync(self, text: str) -> bytes:
        """
        Synthesize using Google Text-to-Speech
        
        Args:
            text: Text to synthesize
        
        Returns:
            Audio bytes (MP3)
        """
        try:
            # Limit text length for gTTS
            if len(text) > 300:
                text = text[:300] + "..."
            
            tts = gTTS(text=text, lang=self.language, slow=False)
            
            # Save to bytes buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            return audio_buffer.getvalue()
        
        except Exception as e:
            logger.error(f"gTTS error: {e}")
            return b""
    
    @staticmethod
    def split_long_text(text: str, max_length: int = 300) -> list[str]:
        """
        Split long text into chunks for TTS
        
        Args:
            text: Long text to split
            max_length: Maximum length per chunk
        
        Returns:
            List of text chunks
        """
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        for sentence in text.split("."):
            if len(current_chunk) + len(sentence) <= max_length:
                current_chunk += sentence + "."
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence + "."
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
