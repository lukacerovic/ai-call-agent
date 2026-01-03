# 🚀 AI Call Agent - Complete Setup Guide

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (Local Development)](#quick-start-local-development)
3. [Docker Setup](#docker-setup)
4. [Configuration](#configuration)
5. [Troubleshooting](#troubleshooting)
6. [First Call](#first-call)

---

## 📦 Prerequisites

### System Requirements

- **OS**: Windows, macOS, or Linux
- **Python**: 3.10 or 3.11 (NOT 3.12+)
- **Node.js**: 18+ (for frontend)
- **npm**: 9+ or yarn
- **ffmpeg**: For audio processing (optional)

### API Keys Required

1. **OpenAI API Key** - For STT (Whisper) and TTS
   - Get it: https://platform.openai.com/api-keys
   - Budget: ~$0.01-0.05 per call

2. **Groq API Key** (Optional - for LLM)
   - Get it: https://groq.com/
   - Free tier available with LLaMA 3.2

### Windows-Specific

If you're on Windows and want to use PyAudio:

```bash
# Install pre-built wheel
pip install pipwin
pipwin install pyaudio
```

**Or skip PyAudio** (it's optional for this project).

---

## ⚡ Quick Start (Local Development)

### Step 1: Clone & Navigate

```bash
git clone https://github.com/lukacerovic/ai-call-agent.git
cd ai-call-agent
```

### Step 2: Backend Setup

#### Windows:

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### macOS/Linux:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env with your keys
# On Windows: notepad .env
# On macOS/Linux: nano .env
```

**Minimal .env setup:**

```env
OPENAI_API_KEY=sk-your-openai-key-here
GROQ_API_KEY=gsk-your-groq-key-here
GROQ_MODEL=llama-3.2-70b-versatile
DEBUG=True
```

### Step 4: Run Backend

```bash
# From backend directory with venv activated
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

✅ You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Test backend health:**
```bash
curl http://localhost:8000/health
```

### Step 5: Frontend Setup (New Terminal/Tab)

```bash
cd frontend
npm install
npm start
```

✅ Browser opens automatically at `http://localhost:3000`

### Step 6: Test the Call

1. Click **"📞 Call Clinic"** button
2. Allow microphone access
3. Listen to AI greeting
4. Speak naturally into your microphone
5. Let it respond

---

## 🐳 Docker Setup

### Prerequisites

- Docker Desktop installed
- `.env` file configured (see Configuration section)

### Run with Docker Compose

```bash
# From project root
docker-compose up --build
```

**What starts:**
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Ollama (optional LLM): http://localhost:11434

### To stop:

```bash
docker-compose down
```

### View logs:

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

---

## ⚙️ Configuration

### Environment Variables

Create `backend/.env` based on `backend/.env.example`:

```env
# === REQUIRED ===
# OpenAI API Key - Get from https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-key-here

# === LLM PROVIDER (Choose one) ===
# Option 1: Use Groq (Recommended)
GROQ_API_KEY=gsk-your-groq-key-here
GROQ_MODEL=llama-3.2-70b-versatile

# Option 2: Use Ollama (Local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# === OPTIONAL ===
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True
LOG_LEVEL=INFO

# Frontend
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Audio
SAMPLE_RATE=16000
CHUNK_SIZE=1024
VAD_THRESHOLD=0.5
SILENCE_DURATION=1.5

# TTS Provider
TTS_PROVIDER=gtts  # Options: gtts, pyttsx3
TTS_LANGUAGE=en

# Clinic Info
CLINIC_NAME=Medical Clinic
CLINIC_PHONE=+1-555-0100
```

### Getting API Keys

#### OpenAI (Required)

1. Go to https://platform.openai.com/api-keys
2. Click "+ Create new secret key"
3. Copy and paste into `.env`
4. Add to billing: https://platform.openai.com/account/billing/overview

#### Groq (Recommended for LLM)

1. Sign up: https://groq.com/
2. Get API key from dashboard
3. Free tier includes LLaMA 3.2 with generous limits

#### Ollama (Free, Local Alternative)

**macOS/Linux:**
```bash
brew install ollama
ollama pull llama2
ollama serve  # Runs on http://localhost:11434
```

**Windows:**
- Download: https://ollama.com/download/windows
- Then: `ollama pull llama2`
- Run: `ollama serve`

---

## 🐛 Troubleshooting

### Backend Issues

#### ❌ "ModuleNotFoundError: No module named 'openai'"

```bash
# Make sure venv is activated
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Reinstall
pip install -r requirements.txt
```

#### ❌ "Could not find a version that satisfies the requirement"

This means you have Python 3.12+. Install Python 3.10 or 3.11:

```bash
# macOS
brew install python@3.11
python3.11 -m venv venv

# Windows - Download from python.org or:
choco install python311

# Linux
sudo apt-get install python3.11 python3.11-venv
python3.11 -m venv venv
```

#### ❌ "OPENAI_API_KEY not found"

```bash
# Check .env file exists in backend directory
ls backend/.env  # macOS/Linux
dir backend\.env  # Windows

# Verify it has your key:
cat backend/.env | grep OPENAI  # macOS/Linux
type backend\.env | findstr OPENAI  # Windows
```

#### ❌ "Connection refused" on localhost:8000

```bash
# Backend not running. In backend directory:
uvicorn main:app --reload

# Check if port 8000 is in use:
# Windows:
netstat -ano | findstr :8000

# macOS/Linux:
lsof -i :8000
```

#### ❌ "Transcription error" or no STT working

- Verify OpenAI API key is correct
- Check your OpenAI billing: https://platform.openai.com/account/usage/overview
- Ensure you have credits (not free trial expired)

### Frontend Issues

#### ❌ "Cannot GET /"

```bash
# Frontend not running. In frontend directory:
npm start
```

#### ❌ "WebSocket connection failed"

```bash
# Backend not responding. Check:
# 1. Backend is running on port 8000
# 2. In browser console: Check error messages
# 3. CORS allowed in backend/.env:
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

#### ❌ "Microphone permission denied"

- **Chrome/Edge**: Click camera icon in address bar → Allow microphone
- **Firefox**: Click lock icon → Allow microphone
- **Safari**: System Settings → Privacy & Security → Microphone

#### ❌ "No audio output"

- Check browser volume (not muted)
- Check computer volume
- Allow audio playback in browser permissions

### Audio Issues

#### ❌ PyAudio installation fails on Windows

PyAudio is optional. Skip it:

```bash
# Edit requirements.txt, remove line:
# pyaudio==0.2.13

pip install -r requirements.txt
```

#### ❌ Microphone not detected

```bash
# Test microphone access:
# Windows: Settings → Privacy & Security → Microphone
# macOS: System Settings → Privacy & Security → Microphone
# Linux: Check pavucontrol or pactl
```

---

## 🎯 First Call - Step by Step

### 1. Start All Services

**Terminal 1 (Backend):**
```bash
cd ai-call-agent/backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload
```

**Terminal 2 (Frontend):**
```bash
cd ai-call-agent/frontend
npm start
```

### 2. Open Browser

Go to `http://localhost:3000`

### 3. Make Your Call

1. **Click "📞 Call Clinic"**
   - Browser requests microphone permission → Click "Allow"
   - Status changes to "Connecting to clinic..."
   - Then "Listening to clinic agent..."

2. **Hear the AI Greeting**
   - "Hello, thank you for calling [Clinic Name]..."
   - Audio plays automatically

3. **Speak Your Message**
   - After greeting, microphone activates
   - Speak clearly (in English)
   - System detects when you stop (silence > 1.5 seconds)
   - Speech converts to text

4. **AI Responds**
   - Backend processes your text
   - Generates professional response
   - Converts to speech
   - Audio plays
   - Cycle repeats

5. **End the Call**
   - Say "Goodbye" or "Thank you"
   - Click "📞 End Call" button
   - Call disconnects

### Example Conversation

```
AI: "Hello, thank you for calling our clinic. I'm an AI assistant. 
How can I help you today?"

You: "I'd like to book an appointment."

AI: "Great! I'd be happy to help you schedule an appointment. 
What service are you interested in?"

You: "I want an initial consultation."

AI: "Perfect. Initial consultation is available. 
What date would work for you?"

You: "January 15th at 2 PM."

AI: "Excellent. Let me confirm: January 15th at 2 PM for an initial consultation. 
May I have your full name?"

You: "John Smith"

AI: "Thank you, John. Your appointment is confirmed for January 15th at 2 PM. 
Have a great day!"
```

---

## 📝 Customization

### Add Your Clinic Info

Edit `backend/.env`:
```env
CLINIC_NAME=Your Clinic Name
CLINIC_PHONE=+1-555-YOUR-PHONE
```

### Add Medical Services

Edit `backend/data/services.json`:
```json
[
  {
    "id": "service-001",
    "name": "Your Service Name",
    "durationMinutes": 30,
    "price": 100,
    "description": "Description of service",
    "whatIsIncluded": "What's included",
    "howItsDone": "How it's done",
    "specialPreparation": "Any prep needed"
  }
]
```

### Customize AI Behavior

Edit `backend/agents/clinic_agent.py` - Modify the system prompt in `_build_system_prompt()` method.

---

## 🔗 Useful Links

- **OpenAI API**: https://platform.openai.com/
- **Groq Console**: https://console.groq.com/
- **FastAPI Docs**: http://localhost:8000/docs (when running)
- **React Documentation**: https://react.dev/
- **WebSocket Guide**: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket

---

## 📞 Support

For issues:

1. Check [Troubleshooting](#troubleshooting) section
2. Check backend logs: `http://localhost:8000/docs`
3. Open GitHub issue: https://github.com/lukacerovic/ai-call-agent/issues

---

**Happy coding! 🎉**
