"""Speech-to-Text module - Audio Transcription using OpenAI Whisper"""

import os
import ssl
import logging
import tempfile
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Fix SSL certificate issues
ssl._create_default_https_context = ssl._create_unverified_context

logger = logging.getLogger(__name__)

# Try to import whisper
try:
    import whisper
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False
    print("\n" + "!" * 80)
    print("❌ OpenAI Whisper not installed!")
    print("Install with: pip install openai-whisper")
    print("!" * 80 + "\n")

# Try to import OpenAI client
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


class SpeechToText:
    """Converts audio bytes to text using OpenAI Whisper"""
    
    def __init__(self):
        """
        Initialize Speech-to-Text module
        
        Tries two approaches:
        1. Local Whisper model (if installed)
        2. OpenAI API (if OPENAI_API_KEY set)
        """
        self.whisper_model = None
        self.openai_client = None
        self.provider = None
        self.is_available = False
        
        # Try local Whisper first (works offline, no API key needed)
        if HAS_WHISPER:
            try:
                logger.info("\n" + "=" * 80)
                logger.info("📥 [STT] Loading local Whisper model...")
                logger.info("=" * 80)
                
                self.whisper_model = whisper.load_model("base")
                self.provider = "whisper_local"
                self.is_available = True
                
                logger.info("✅ [STT] Local Whisper model loaded successfully")
                logger.info(f"🗣️  [STT] Provider: {self.provider} (offline)")
                logger.info("=" * 80 + "\n")
                return
            
            except Exception as e:
                logger.warning(f"⚠️  [STT] Failed to load local Whisper: {e}")
                self.whisper_model = None
        
        # Fall back to OpenAI API
        api_key = os.getenv("OPENAI_API_KEY")
        if HAS_OPENAI and api_key:
            try:
                logger.info("\n" + "=" * 80)
                logger.info("📥 [STT] Initializing OpenAI Whisper API...")
                logger.info("=" * 80)
                
                self.openai_client = OpenAI(api_key=api_key)
                self.provider = "whisper_api"
                self.is_available = True
                
                logger.info("✅ [STT] OpenAI Whisper API ready")
                logger.info(f"🗣️  [STT] Provider: {self.provider} (requires API key)")
                logger.info("=" * 80 + "\n")
                return
            
            except Exception as e:
                logger.warning(f"⚠️  [STT] Failed to initialize OpenAI: {e}")
                self.openai_client = None
        
        # If we reach here, no STT provider is available
        logger.error("\n" + "!" * 80)
        logger.error("❌ [STT] No Speech-to-Text provider available!")
        logger.error("")
        logger.error("Option 1: Install local Whisper (offline, recommended)")
        logger.error("  pip install openai-whisper")
        logger.error("")
        logger.error("Option 2: Set OPENAI_API_KEY for API-based Whisper")
        logger.error("  export OPENAI_API_KEY=sk-...")
        logger.error("!" * 80 + "\n")
        self.is_available = False
    
    async def transcribe(self, audio_bytes: bytes) -> str:
        """
        Transcribe audio bytes to text
        
        Args:
            audio_bytes: Raw audio data (WAV, WebM, or other format)
        
        Returns:
            Transcribed text string (empty if fails)
        """
        if not self.is_available:
            logger.error("❌ [STT] Transcription not available")
            return ""
        
        if not audio_bytes or len(audio_bytes) == 0:
            logger.warning("⚠️  [STT] No audio data provided")
            return ""
        
        try:
            logger.info("\n" + "=" * 80)
            logger.info(f"📥 [STT] Transcribing audio ({len(audio_bytes)} bytes)...")
            logger.info(f"🗣️  [STT] Provider: {self.provider}")
            logger.info("=" * 80)
            
            if self.provider == "whisper_local":
                result = await self._transcribe_whisper_local(audio_bytes)
            elif self.provider == "whisper_api":
                result = await self._transcribe_whisper_api(audio_bytes)
            else:
                logger.error("❌ [STT] Unknown provider")
                return ""
            
            if result.strip():
                logger.info(f"✅ [STT] Transcription: '{result}'")
                logger.info("=" * 80 + "\n")
                return result.strip()
            else:
                logger.warning("⚠️  [STT] Transcription returned empty text")
                logger.warning("Possible causes: Audio too quiet, silence only, wrong language")
                logger.info("=" * 80 + "\n")
                return ""
        
        except Exception as e:
            logger.error(f"❌ [STT] Transcription error: {e}")
            import traceback
            traceback.print_exc()
            logger.info("=" * 80 + "\n")
            return ""
    
    async def _transcribe_whisper_local(self, audio_bytes: bytes) -> str:
        """
        Transcribe using local Whisper model (offline)
        
        Args:
            audio_bytes: Raw audio data
        
        Returns:
            Transcribed text
        """
        try:
            logger.debug("🔄 [STT:Local] Processing audio...")
            
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_path = tmp_file.name
            
            logger.debug(f"📁 [STT:Local] Temp file: {tmp_path}")
            
            try:
                logger.debug("🔄 [STT:Local] Running Whisper transcription...")
                
                # Transcribe audio
                result = self.whisper_model.transcribe(tmp_path)
                text = result.get("text", "").strip()
                
                logger.debug(f"📝 [STT:Local] Raw result: '{text}'")
                return text
            
            finally:
                # Clean up temporary file
                try:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                        logger.debug(f"🗑️  [STT:Local] Temp file deleted")
                except Exception as e:
                    logger.warning(f"⚠️  [STT:Local] Failed to delete temp file: {e}")
        
        except Exception as e:
            logger.error(f"❌ [STT:Local] Error: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    async def _transcribe_whisper_api(self, audio_bytes: bytes) -> str:
        """
        Transcribe using OpenAI Whisper API
        
        Args:
            audio_bytes: Raw audio data
        
        Returns:
            Transcribed text
        """
        try:
            logger.debug("🔄 [STT:API] Processing audio...")
            
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_path = tmp_file.name
            
            logger.debug(f"📁 [STT:API] Temp file: {tmp_path}")
            
            try:
                logger.debug("🔄 [STT:API] Calling OpenAI Whisper API...")
                
                # Open file and transcribe
                with open(tmp_path, "rb") as audio_file:
                    transcript = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                
                text = transcript.text.strip()
                logger.debug(f"📝 [STT:API] Raw result: '{text}'")
                return text
            
            finally:
                # Clean up temporary file
                try:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                        logger.debug(f"🗑️  [STT:API] Temp file deleted")
                except Exception as e:
                    logger.warning(f"⚠️  [STT:API] Failed to delete temp file: {e}")
        
        except Exception as e:
            logger.error(f"❌ [STT:API] Error: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def transcribe_sync(self, audio_bytes: bytes) -> str:
        """
        Synchronous (blocking) transcription
        
        Args:
            audio_bytes: Raw audio data
        
        Returns:
            Transcribed text
        """
        if not self.is_available:
            logger.error("❌ [STT] Transcription not available")
            return ""
        
        if not audio_bytes or len(audio_bytes) == 0:
            logger.warning("⚠️  [STT] No audio data provided")
            return ""
        
        try:
            logger.info(f"📥 [STT] Transcribing {len(audio_bytes)} bytes (sync)...")
            
            if self.provider == "whisper_local":
                # Save audio to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                    tmp_file.write(audio_bytes)
                    tmp_path = tmp_file.name
                
                try:
                    result = self.whisper_model.transcribe(tmp_path)
                    text = result.get("text", "").strip()
                    logger.debug(f"✅ [STT:Local:Sync] Transcription: '{text}'")
                    return text
                
                finally:
                    try:
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)
                    except:
                        pass
            
            elif self.provider == "whisper_api":
                # Save audio to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                    tmp_file.write(audio_bytes)
                    tmp_path = tmp_file.name
                
                try:
                    with open(tmp_path, "rb") as audio_file:
                        transcript = self.openai_client.audio.transcriptions.create(
                            model="whisper-1",
                            file=audio_file
                        )
                    
                    text = transcript.text.strip()
                    logger.debug(f"✅ [STT:API:Sync] Transcription: '{text}'")
                    return text
                
                finally:
                    try:
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)
                    except:
                        pass
        
        except Exception as e:
            logger.error(f"❌ [STT] Sync transcription error: {e}")
        
        return ""
