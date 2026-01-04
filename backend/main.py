"""FastAPI backend for AI Call Agent - Medical Clinic Voice Support System

Simplified architecture:
- Frontend: Handles audio capture, VAD, transcription, TTS
- Backend: Handles only text-based chat and AI agent processing
"""

import os
import json
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from agents.clinic_agent import ClinicAgent

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

clinic_agent = None


class ChatRequest(BaseModel):
    """Chat message request model"""
    session_id: str
    message: str


class ChatResponse(BaseModel):
    """Chat message response model"""
    session_id: str
    response: str
    success: bool = True


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    global clinic_agent
    logger.info("\n" + "=" * 80)
    logger.info("🏥 AI Call Agent Backend Starting...")
    logger.info("=" * 80)
    
    try:
        clinic_agent = ClinicAgent()
        logger.info("✅ Clinic agent initialized")
        logger.info("✅ System ready to receive calls")
        logger.info("=" * 80 + "\n")
    except Exception as e:
        logger.error(f"❌ Failed to initialize agent: {e}")
        logger.info("=" * 80 + "\n")
        raise
    
    yield
    
    # Shutdown
    logger.info("\n" + "=" * 80)
    logger.info("🛑 AI Call Agent Backend Shutting Down...")
    logger.info("=" * 80 + "\n")


# Initialize FastAPI app
app = FastAPI(
    title="AI Call Agent",
    description="Medical clinic voice support system with AI agent",
    version="2.0.0 - Client-Side Voice Processing",
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
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "architecture": "Client-side voice processing"
    }


# ============================================================================
# Session Management
# ============================================================================

@app.get("/session/new")
async def create_new_session():
    """Create a new conversation session
    
    Called by frontend when user initiates a call.
    Returns unique session_id for tracking conversation.
    """
    print("\n" + "-" * 80)
    print("🆕 NEW SESSION REQUEST")
    print("-" * 80)
    try:
        session_id = str(uuid4())
        sessions[session_id] = {
            "created_at": datetime.now().isoformat(),
            "messages": []
        }
        print(f"✅ Session created: {session_id}")
        print(f"💾 Session stored in memory")
        print("-" * 80 + "\n")
        return {
            "session_id": session_id,
            "status": "created"
        }
    except Exception as e:
        print(f"❌ Session creation failed: {e}")
        import traceback
        traceback.print_exc()
        print("-" * 80 + "\n")
        raise HTTPException(status_code=500, detail=f"Session error: {str(e)}")


# ============================================================================
# Chat/AI Processing (TEXT ONLY)
# ============================================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process user text through AI agent and return text response
    
    Data Flow:
    1. Frontend captures audio from microphone
    2. Frontend detects silence (VAD) and stops recording
    3. Frontend transcribes audio using Web Speech API
    4. Frontend sends transcribed text to this endpoint
    5. Backend processes text through Ollama AI agent
    6. Backend returns response text
    7. Frontend converts response text to speech (TTS)
    8. Loop continues
    
    Args:
        request: ChatRequest with session_id and message text
    
    Returns:
        ChatResponse with response text
    """
    try:
        print("\n" + "=" * 80)
        print("💬 [CHAT] Processing user message")
        print("=" * 80)
        print(f"👤 User: '{request.message}'")
        print(f"🎫 Session: {request.session_id}")
        
        # Validate session
        if request.session_id not in sessions:
            print(f"❌ [CHAT] Session not found: {request.session_id}")
            print("=" * 80 + "\n")
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Store user message in session
        sessions[request.session_id]["messages"].append({
            "role": "user",
            "text": request.message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Process through clinic agent
        print(f"\n🧠 [CHAT] Sending to AI agent...")
        response_text = clinic_agent.process_message(
            user_message=request.message,
            session_id=request.session_id
        )
        
        # Store assistant response in session
        sessions[request.session_id]["messages"].append({
            "role": "assistant",
            "text": response_text,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"\n🤖 [CHAT] AI Response: '{response_text}'")
        print("=" * 80 + "\n")
        
        return ChatResponse(
            session_id=request.session_id,
            response=response_text,
            success=True
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n❌ [CHAT] Error: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 80 + "\n")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


# ============================================================================
# Services Endpoint
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
