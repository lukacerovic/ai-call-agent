"""FastAPI backend for AI Call Agent - Medical Clinic Voice Support System"""

import os
import json
import logging
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from agents.clinic_agent import ClinicAgent
from audio.stt import SpeechToText
from audio.tts import TextToSpeech
from audio.vad import VoiceActivityDetector

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize components - handle gracefully if dependencies fail
try:
    stt = SpeechToText()
    logger.info("✅ STT initialized (OpenAI Whisper) - STT will be available if OPENAI_API_KEY is set")
except Exception as e:
    logger.warning(f"⚠️  STT initialization failed: {e}")
    stt = SpeechToText()  # Will be disabled gracefully

try:
    tts = TextToSpeech()
    logger.info("✅ TTS initialized (gTTS)")
except Exception as e:
    logger.error(f"❌ TTS initialization failed: {e}")
    raise  # TTS is critical

try:
    vad = VoiceActivityDetector()
    logger.info("✅ VAD initialized")
except Exception as e:
    logger.error(f"❌ VAD initialization failed: {e}")
    raise  # VAD is critical

clinic_agent = None


class ReservationRequest(BaseModel):
    """Model for booking a reservation"""
    service_id: str
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    patient_name: str
    patient_dob: str  # YYYY-MM-DD


class ReservationResponse(BaseModel):
    """Model for reservation response"""
    success: bool
    message: str
    reservation_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    global clinic_agent
    logger.info("🏥 AI Call Agent starting...")
    
    try:
        clinic_agent = ClinicAgent()
        logger.info("✅ Clinic agent initialized")
        logger.info("✅ System ready to receive calls")
    except Exception as e:
        logger.error(f"❌ Failed to initialize agent: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 AI Call Agent shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="AI Call Agent",
    description="Medical clinic voice support system with AI agent",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health Check Endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check if the system is running"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat()
    )


# Services Endpoint
@app.get("/services")
async def get_services():
    """Get list of available medical services"""
    try:
        services_path = os.path.join(
            os.path.dirname(__file__),
            "data",
            "services.json"
        )
        with open(services_path, "r") as f:
            services = json.load(f)
        return {"success": True, "services": services}
    except FileNotFoundError:
        logger.error("services.json not found")
        raise HTTPException(status_code=500, detail="Services data not found")
    except Exception as e:
        logger.error(f"Error loading services: {e}")
        raise HTTPException(status_code=500, detail="Error loading services")


# Reservations Endpoint
@app.post("/reservations", response_model=ReservationResponse)
async def create_reservation(request: ReservationRequest):
    """Create a new reservation"""
    try:
        reservations_path = os.path.join(
            os.path.dirname(__file__),
            "data",
            "reservations.json"
        )
        
        # Load existing reservations
        with open(reservations_path, "r") as f:
            reservations = json.load(f)
        
        # Create new reservation
        new_reservation = {
            "id": f"res-{datetime.now().timestamp()}",
            "serviceId": request.service_id,
            "date": request.date,
            "time": request.time,
            "patientName": request.patient_name,
            "patientDOB": request.patient_dob,
            "createdAt": datetime.now().isoformat()
        }
        
        reservations.append(new_reservation)
        
        # Save updated reservations
        with open(reservations_path, "w") as f:
            json.dump(reservations, f, indent=2)
        
        logger.info(f"✅ Reservation created: {new_reservation['id']}")
        
        return ReservationResponse(
            success=True,
            message=f"Reservation confirmed for {request.patient_name} on {request.date} at {request.time}",
            reservation_id=new_reservation["id"]
        )
    except Exception as e:
        logger.error(f"Error creating reservation: {e}")
        raise HTTPException(status_code=500, detail="Error creating reservation")


# WebSocket Endpoint - Main Voice Call
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time voice interaction"""
    await websocket.accept()
    logger.info("📞 New call connected")
    
    session_id = f"session-{datetime.now().timestamp()}"
    message_count = 0
    
    try:
        # Send initial greeting
        greeting = clinic_agent.get_greeting()
        logger.info(f"🎤 Agent: {greeting}")
        
        # Convert greeting to speech
        audio_data = await tts.synthesize(greeting)
        logger.debug(f"📤 Sending greeting audio: {len(audio_data)} bytes")
        await websocket.send_bytes(audio_data)
        
        # Main conversation loop
        logger.info("🎧 Waiting for user audio...")
        while True:
            try:
                # Receive audio chunk from client
                logger.debug("📥 Receiving from WebSocket...")
                data = await websocket.receive_bytes()
                
                logger.debug(f"📊 Received audio chunk: {len(data)} bytes")
                
                if not data:
                    logger.debug("⚠️  Empty audio data received")
                    continue
                
                # Voice Activity Detection
                logger.debug("🔍 Running Voice Activity Detection...")
                is_speech = vad.detect(data)
                logger.debug(f"🔍 VAD result: {is_speech} (speech detected: {is_speech})")
                
                if not is_speech:
                    logger.debug("🔇 Silence detected, continuing to listen...")
                    continue
                
                # Speech to Text (only if available)
                logger.debug("🎤 Starting Speech-to-Text...")
                if stt.is_available:
                    logger.debug(f"📝 STT Provider: {stt.provider}")
                    user_text = await stt.transcribe(data)
                    logger.debug(f"📝 Transcription result: '{user_text}'")
                else:
                    logger.warning("⚠️  STT not available, skipping speech-to-text")
                    user_text = "[audio received but not transcribed]"
                
                logger.info(f"👤 User: {user_text}")
                
                if not user_text or "[audio" in user_text.lower():
                    logger.debug("⏭️  Skipping empty transcription, continuing to listen...")
                    continue
                
                # Check for end of call
                if clinic_agent.should_end_call(user_text):
                    farewell = clinic_agent.get_farewell()
                    logger.info(f"🎤 Agent: {farewell}")
                    audio_data = await tts.synthesize(farewell)
                    await websocket.send_bytes(audio_data)
                    break
                
                # Process through AI Agent
                logger.debug(f"🧠 Sending to agent: '{user_text}'")
                response = clinic_agent.process_message(
                    user_message=user_text,
                    session_id=session_id
                )
                logger.info(f"🎤 Agent: {response}")
                
                # Text to Speech
                logger.debug("🔊 Converting response to speech...")
                audio_data = await tts.synthesize(response)
                logger.debug(f"📤 Sending response audio: {len(audio_data)} bytes")
                await websocket.send_bytes(audio_data)
                
                message_count += 1
                logger.debug(f"✅ Message #{message_count} completed")
                
            except Exception as e:
                logger.error(f"❌ Error in message processing loop: {e}", exc_info=True)
                # Continue listening despite errors
                continue
            
    except WebSocketDisconnect:
        logger.info("📞 Call disconnected")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass
    finally:
        logger.info(f"📊 Call session {session_id} ended (messages processed: {message_count})")


# Debug Endpoints (Development Only)
if os.getenv("DEBUG", "False") == "True":
    
    @app.post("/debug/tts")
    async def debug_tts(text: str):
        """Test TTS conversion"""
        try:
            audio = await tts.synthesize(text)
            return {
                "success": True,
                "text": text,
                "audio_length": len(audio)
            }
        except Exception as e:
            logger.error(f"TTS error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/debug/stt")
    async def debug_stt(file: UploadFile = File(...)):
        """Test STT conversion"""
        try:
            if not stt.is_available:
                raise HTTPException(
                    status_code=503,
                    detail="STT not available - set OPENAI_API_KEY to enable"
                )
            
            audio_data = await file.read()
            text = await stt.transcribe(audio_data)
            return {
                "success": True,
                "text": text,
                "confidence": 0.95  # Mock confidence
            }
        except Exception as e:
            logger.error(f"STT error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/debug/agent-context")
    async def debug_agent_context(session_id: str):
        """Get agent context for debugging"""
        try:
            context = clinic_agent.get_conversation_context(session_id)
            return {
                "success": True,
                "context": context
            }
        except Exception as e:
            logger.error(f"Context error: {e}")
            raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🚀 Starting server on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "False") == "True"
    )
