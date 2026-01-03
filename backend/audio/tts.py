"""Text-to-Speech module using gTTS (Google Text-to-Speech) - No API key needed"""

import os
import io
import logging
from typing import Optional, List
from enum import Enum
from dotenv import load_dotenv

try:
    from gtts import gTTS
except ImportError:
    print("gTTS not installed. Install with: pip install gtts")

try:
    import pyttsx3
except ImportError:
    print("pyttsx3 not installed. Install with: pip install pyttsx3")

load_dotenv()

logger = logging.getLogger(__name__)


class TTSProvider(str, Enum):
    """Available TTS providers (all free, no API key needed)"""
    GTTS = "gtts"  # Google Text-to-Speech (best quality, needs internet)
    PYTTSX3 = "pyttsx3"  # Local TTS (works offline, lower quality)


class TextToSpeech:
    """Converts text to speech audio using free providers (no API key required)"""
    
    def __init__(
        self,
        provider: str = "gtts",
        language: str = "en",
        speed: float = 1.0
    ):
        """
        Initialize Text-to-Speech converter
        
        Args:
            provider: TTS provider ("gtts" or "pyttsx3")
                - "gtts": Google Text-to-Speech (better quality, needs internet)
                - "pyttsx3": Local synthesis (works offline, lower quality)
            language: Language code (e.g., "en" for English)
            speed: Speech speed (only for pyttsx3: 0.5-2.0)
        """
        self.provider = os.getenv("TTS_PROVIDER", provider).lower()
        self.language = language
        self.speed = speed
        self.is_available = False
        self.engine = None
        
        # Validate provider
        if self.provider not in ["gtts", "pyttsx3"]:
            logger.warning(f"Unknown provider: {self.provider}, defaulting to gtts")
            self.provider = "gtts"
        
        # Initialize based on provider
        try:
            if self.provider == "pyttsx3":
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', int(150 * self.speed))  # Speed in WPM
                logger.info(f"✅ TTS initialized with provider: pyttsx3 (local, offline)")
            else:  # gtts
                logger.info(f"✅ TTS initialized with provider: gtts (Google, needs internet)")
            
            self.is_available = True
        except Exception as e:
            logger.error(f"Error initializing TTS: {e}")
            logger.warning("TTS will not work - check if gtts/pyttsx3 are properly installed")
            self.is_available = False
    
    async def synthesize(self, text: str) -> bytes:
        """
        Convert text to speech audio (async)
        
        Args:
            text: Text to convert to speech
        
        Returns:
            Audio data as bytes (MP3 format for gTTS, WAV for pyttsx3)
        """
        if not self.is_available:
            logger.warning("TTS not available")
            return b""
        
        try:
            if self.provider == "pyttsx3":
                return self._synthesize_pyttsx3_sync(text)
            else:  # gtts
                return self._synthesize_gtts_sync(text)
        
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return b""
    
    def synthesize_sync(self, text: str) -> bytes:
        """
        Convert text to speech audio (synchronous)
        
        Args:
            text: Text to convert to speech
        
        Returns:
            Audio data as bytes (MP3 format for gTTS, WAV for pyttsx3)
        """
        if not self.is_available:
            logger.warning("TTS not available")
            return b""
        
        try:
            if self.provider == "pyttsx3":
                return self._synthesize_pyttsx3_sync(text)
            else:  # gtts
                return self._synthesize_gtts_sync(text)
        
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return b""
    
    def _synthesize_gtts_sync(self, text: str) -> bytes:
        """
        Synthesize using Google Text-to-Speech
        
        Args:
            text: Text to synthesize
        
        Returns:
            Audio bytes (MP3)
        """
        try:
            # Limit text length for gTTS (max ~300 chars per request)
            if len(text) > 300:
                text = text[:300] + "..."
            
            # Create gTTS object
            tts = gTTS(text=text, lang=self.language, slow=False)
            
            # Save to bytes buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            logger.debug(f"gTTS synthesized {len(text)} characters")
            return audio_buffer.getvalue()
        
        except Exception as e:
            logger.error(f"gTTS error: {e}")
            return b""
    
    def _synthesize_pyttsx3_sync(self, text: str) -> bytes:
        """
        Synthesize using pyttsx3 (local, offline)
        
        Args:
            text: Text to synthesize
        
        Returns:
            Audio bytes (WAV format)
        """
        try:
            if not self.engine:
                logger.error("pyttsx3 engine not initialized")
                return b""
            
            # Create temporary file for audio
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_path = f.name
            
            try:
                # Generate speech
                self.engine.save_to_file(text, temp_path)
                self.engine.runAndWait()
                
                # Read the file
                with open(temp_path, "rb") as f:
                    audio_data = f.read()
                
                logger.debug(f"pyttsx3 synthesized {len(text)} characters")
                return audio_data
            
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except:
                    pass
        
        except Exception as e:
            logger.error(f"pyttsx3 error: {e}")
            return b""
    
    @staticmethod
    def split_long_text(text: str, max_length: int = 300) -> List[str]:
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
        
        # Split by sentences
        sentences = text.replace("! ", "!\n").replace("? ", "?\n").split("\n")
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            if len(current_chunk) + len(sentence) + 1 <= max_length:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
