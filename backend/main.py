"""FastAPI backend for AI Call Agent - Medical Clinic Voice Support System
Refactored to match proven ai-medical-agent data flow
"""

import os
import json
import logging
import tempfile
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
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

# Session storage (in-memory for now)
sessions = {}

# Initialize components
try:
    stt = SpeechToText()
    logger.info("✅ STT initialized (OpenAI Whisper)")
except Exception as e:
    logger.warning(f"⚠️  STT initialization failed: {e}")
    stt = SpeechToText()

try:
    tts = TextToSpeech()
    logger.info("✅ TTS initialized (gTTS)")
except Exception as e:
    logger.error(f"❌ TTS initialization failed: {e}")
    raise

try:
    vad = VoiceActivityDetector()
    logger.info("✅ VAD initialized")
except Exception as e:
    logger.error(f"❌ VAD initialization failed: {e}")
    raise

clinic_agent = None


class ChatRequest(BaseModel):
    """Chat message request model"""
    session_id: str
    text: str


class ChatResponse(BaseModel):
    """Chat message response model"""
    session_id: str
    assistant_response: str
    success: bool = True


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


# ============================================================================
# Session Management Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.get("/session/new")
async def create_new_session():
    """Create a new conversation session"""
    print("\n" + "-" * 80)
    print("🆕 NEW SESSION REQUEST")
    print("-" * 80)
    try:
        session_id = str(uuid4())
        sessions[session_id] = {
            "created_at": datetime.now().isoformat(),
            "messages": []
        }
        print(f"✅ Session created successfully: {session_id}")
        print(f"💾 Session stored in memory")
        print("-" * 80 + "\n")
        return {
            "session_id": session_id,
            "status": "created"
        }
    except Exception as e:
        print(f"❌ Session creation error: {e}")
        import traceback
        traceback.print_exc()
        print("-" * 80 + "\n")
        return {
            "error": str(e),
            "status": "failed"
        }


# ============================================================================
# Audio Transcription Endpoint
# ============================================================================

@app.post("/api/transcribe")
async def transcribe_audio(audio: UploadFile = File(...), session_id: str = Form(...)):
    """Transcribe audio file to text using Speech-to-Text
    
    Expected flow:
    1. Frontend captures audio as WebM blob
    2. Sends to /api/transcribe endpoint
    3. Backend transcribes using Google Speech Recognition
    4. Returns transcribed text
    5. Frontend sends text to /api/chat for AI processing
    """
    try:
        print(f"\n📥 [TRANSCRIBE] Received audio for session: {session_id}")
        
        # Save uploaded audio to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_file:
            content = await audio.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        print(f"📁 [TRANSCRIBE] Audio file saved: {len(content)} bytes")
        
        try:
            # Transcribe using STT provider
            print(f"🎤 [TRANSCRIBE] Starting transcription...")
            audio_bytes = open(tmp_path, 'rb').read()
            text = await stt.transcribe(audio_bytes)
            
            print(f"📝 [TRANSCRIBE] Result: '{text}'")
            
            if not text or text.strip() == "":
                print("⚠️  [TRANSCRIBE] Empty transcription returned")
                return {
                    "session_id": session_id,
                    "text": "",
                    "success": False,
                    "error": "Could not transcribe audio"
                }
            
            print(f"✅ [TRANSCRIBE] Transcription successful\n")
            
            return {
                "session_id": session_id,
                "text": text,
                "success": True
            }
        
        finally:
            # Clean up temp file
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    print(f"🗑️  [TRANSCRIBE] Temp file deleted")
            except Exception as e:
                print(f"❌ [TRANSCRIBE] Error deleting temp file: {e}")
    
    except Exception as e:
        print(f"❌ [TRANSCRIBE] Transcription error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")


# ============================================================================
# Chat/AI Processing Endpoint
# ============================================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process user text through AI agent and return response
    
    Expected flow:
    1. Frontend receives transcribed text
    2. Sends to /api/chat with session_id and text
    3. Backend processes through Ollama AI agent
    4. Returns AI response
    5. Frontend converts response to speech (TTS)
    """
    try:
        print("\n" + "=" * 80)
        print("💬 [CHAT] Processing user message")
        print("=" * 80)
        print(f"👤 User: {request.text}")
        print(f"🎫 Session: {request.session_id}")
        
        # Store message in session
        if request.session_id in sessions:
            sessions[request.session_id]["messages"].append({
                "role": "user",
                "text": request.text,
                "timestamp": datetime.now().isoformat()
            })
        
        # Process through clinic agent
        print(f"🧠 [CHAT] Sending to agent...")
        response_text = clinic_agent.process_message(
            user_message=request.text,
            session_id=request.session_id
        )
        
        print(f"🤖 [CHAT] Agent response: {response_text}")
        
        # Store response in session
        if request.session_id in sessions:
            sessions[request.session_id]["messages"].append({
                "role": "assistant",
                "text": response_text,
                "timestamp": datetime.now().isoformat()
            })
        
        print("=" * 80 + "\n")
        
        return ChatResponse(
            session_id=request.session_id,
            assistant_response=response_text,
            success=True
        )
    
    except Exception as e:
        print(f"\n❌ [CHAT] Error: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 80 + "\n")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


# ============================================================================
# Services Endpoints
# ============================================================================

@app.get("/api/services")
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
        return {"success": False, "services": []}
    except Exception as e:
        logger.error(f"Error loading services: {e}")
        return {"success": False, "services": []}


# ============================================================================
# Debug Endpoints (Development Only)
# ============================================================================

if os.getenv("DEBUG", "False") == "True":
    
    @app.get("/debug/sessions")
    async def debug_get_sessions():
        """Get all active sessions (debug only)"""
        return {
            "total_sessions": len(sessions),
            "sessions": list(sessions.keys())
        }
    
    @app.get("/debug/session/{session_id}")
    async def debug_get_session(session_id: str):
        """Get session details (debug only)"""
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        return sessions[session_id]


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
