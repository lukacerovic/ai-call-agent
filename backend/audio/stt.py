"""Speech-to-Text module using OpenAI Whisper"""

import os
import io
import numpy as np
import logging
from typing import Optional
from dotenv import load_dotenv

try:
    from openai import OpenAI, AsyncOpenAI
except ImportError:
    print("OpenAI library not installed. Install with: pip install openai")

load_dotenv()

logger = logging.getLogger(__name__)


class SpeechToText:
    """Converts speech audio to text using OpenAI Whisper"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        language: str = "en",
        model: str = "whisper-1"
    ):
        """
        Initialize Speech-to-Text converter
        
        Args:
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
            language: Language code (default: "en" for English)
            model: Whisper model to use (default: "whisper-1")
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.language = language
        self.model = model
        
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)
        
        logger.info(f"STT initialized with model: {self.model}, language: {self.language}")
    
    async def transcribe(self, audio_data: bytes) -> str:
        """
        Transcribe audio data to text
        
        Args:
            audio_data: Raw audio bytes or numpy array
        
        Returns:
            Transcribed text
        """
        try:
            # Convert audio data
            if isinstance(audio_data, np.ndarray):
                audio_bytes = audio_data.astype(np.int16).tobytes()
            else:
                audio_bytes = audio_data
            
            # Create file-like object
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "audio.wav"
            
            # Transcribe using OpenAI Whisper
            transcript = await self.async_client.audio.transcriptions.create(
                model=self.model,
                file=("audio.wav", audio_file, "audio/wav"),
                language=self.language
            )
            
            text = transcript.text.strip()
            logger.debug(f"Transcribed: {text}")
            
            return text
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""
    
    def transcribe_sync(self, audio_data: bytes) -> str:
        """
        Synchronous version of transcribe
        
        Args:
            audio_data: Raw audio bytes or numpy array
        
        Returns:
            Transcribed text
        """
        try:
            # Convert audio data
            if isinstance(audio_data, np.ndarray):
                audio_bytes = audio_data.astype(np.int16).tobytes()
            else:
                audio_bytes = audio_data
            
            # Create file-like object
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "audio.wav"
            
            # Transcribe using OpenAI Whisper
            transcript = self.client.audio.transcriptions.create(
                model=self.model,
                file=("audio.wav", audio_file, "audio/wav"),
                language=self.language
            )
            
            text = transcript.text.strip()
            logger.debug(f"Transcribed: {text}")
            
            return text
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""
    
    @staticmethod
    def prepare_audio(
        audio_data: np.ndarray,
        sample_rate: int = 16000,
        mono: bool = True
    ) -> np.ndarray:
        """
        Prepare audio data for transcription
        
        Args:
            audio_data: Raw audio data
            sample_rate: Target sample rate
            mono: Convert to mono if True
        
        Returns:
            Prepared audio data
        """
        # Convert to mono if needed
        if mono and len(audio_data.shape) > 1:
            audio_data = np.mean(audio_data, axis=1)
        
        # Normalize audio
        if np.max(np.abs(audio_data)) > 1:
            audio_data = audio_data / np.max(np.abs(audio_data))
        
        return audio_data
