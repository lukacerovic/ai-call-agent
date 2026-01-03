"""Voice Activity Detection (VAD) module using pyannote.audio"""

import os
import numpy as np
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class VoiceActivityDetector:
    """Detects voice activity in audio chunks"""
    
    def __init__(
        self,
        threshold: float = 0.5,
        silence_duration: float = 1.5,
        sample_rate: int = 16000,
        chunk_size: int = 1024
    ):
        """
        Initialize VAD detector
        
        Args:
            threshold: Confidence threshold for speech detection (0-1)
            silence_duration: Required silence duration in seconds to trigger silence detection
            sample_rate: Audio sample rate in Hz
            chunk_size: Audio chunk size
        """
        self.threshold = float(os.getenv("VAD_THRESHOLD", threshold))
        self.silence_duration = float(os.getenv("SILENCE_DURATION", silence_duration))
        self.sample_rate = int(os.getenv("SAMPLE_RATE", sample_rate))
        self.chunk_size = int(os.getenv("CHUNK_SIZE", chunk_size))
        
        self.silence_counter = 0
        self.silence_threshold_samples = int(self.silence_duration * self.sample_rate / self.chunk_size)
        
        logger.info(
            f"VAD initialized - Threshold: {self.threshold}, "
            f"Silence Duration: {self.silence_duration}s, "
            f"Sample Rate: {self.sample_rate}Hz"
        )
    
    def detect(self, audio_chunk: np.ndarray) -> bool:
        """
        Detect voice activity in audio chunk
        
        Args:
            audio_chunk: Audio data as numpy array or bytes
        
        Returns:
            True if speech detected, False if silence
        """
        try:
            # Convert bytes to numpy array if needed
            if isinstance(audio_chunk, bytes):
                audio_chunk = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
            elif isinstance(audio_chunk, np.ndarray) and audio_chunk.dtype == np.int16:
                audio_chunk = audio_chunk.astype(np.float32) / 32768.0
            
            # Simple energy-based VAD
            energy = np.sqrt(np.mean(audio_chunk ** 2))
            
            # Energy threshold for speech detection
            # Typical speech energy is much higher than background noise
            energy_threshold = 0.02
            
            # Additional frequency-based check for more robustness
            # Speech typically has energy in 300-3000 Hz range
            is_speech = energy > energy_threshold
            
            if is_speech:
                self.silence_counter = 0
                return True
            else:
                self.silence_counter += 1
                return False
                
        except Exception as e:
            logger.error(f"VAD error: {e}")
            return False
    
    def has_silence(self) -> bool:
        """
        Check if silence threshold has been reached
        
        Returns:
            True if silence detected for silence_duration seconds
        """
        return self.silence_counter >= self.silence_threshold_samples
    
    def reset(self):
        """Reset silence counter"""
        self.silence_counter = 0
    
    @staticmethod
    def calculate_energy(audio_chunk: np.ndarray) -> float:
        """
        Calculate energy of audio chunk
        
        Args:
            audio_chunk: Audio data as numpy array
        
        Returns:
            Energy level (RMS value)
        """
        return float(np.sqrt(np.mean(audio_chunk ** 2)))
    
    @staticmethod
    def get_zero_crossing_rate(audio_chunk: np.ndarray) -> float:
        """
        Calculate zero crossing rate (useful for voice detection)
        
        Args:
            audio_chunk: Audio data as numpy array
        
        Returns:
            Zero crossing rate
        """
        zcr = np.mean(np.abs(np.diff(np.sign(audio_chunk)))) / 2
        return float(zcr)
