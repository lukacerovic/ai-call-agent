# 📋 Quick Reference - Get Running in 5 Minutes

## ⚡ Your Setup (Ollama - No API Key)

### Terminal 1: Ollama Server
```bash
ollama serve
# Stays running - leave this terminal open
```

### Terminal 2: Pull Model (First Time Only)
```bash
ollama pull llama2  # ~4GB, takes 2-3 minutes
```

### Terminal 3: Backend
```bash
cd backend

# Activate venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Create .env
echo OLLAMA_BASE_URL=http://localhost:11434/v1 > .env
echo OLLAMA_MODEL=llama2 >> .env
echo OLLAMA_API_KEY=ollama >> .env
echo TTS_PROVIDER=gtts >> .env

# Run
uvicorn main:app --reload
```

### Terminal 4: Frontend
```bash
cd frontend
npm start
```

### Browser
```
http://localhost:3000
Click "Call Clinic" button
Allow microphone
Start chatting!
```

---

## 📊 Configuration Files

### `backend/.env` (Create This)
```env
# For Ollama (Local, Free)
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama2
OLLAMA_API_KEY=ollama
TTS_PROVIDER=gtts

# For Groq (Free, Fast)
# GROQ_API_KEY=gsk-your-key-here
# GROQ_MODEL=llama-3.2-70b-versatile

# For OpenAI (Paid)
# OPENAI_API_KEY=sk-your-key-here
```

### `frontend/.env` (Optional)
```env
REACT_APP_API_URL=http://localhost:8000
```

---

## 🌟 Common Commands

### Ollama Commands
```bash
# List installed models
ollama list

# Pull a model
ollama pull llama2
ollama pull mistral  # Faster alternative
ollama pull llama2:13b  # Larger, better quality

# Remove a model
ollama rm llama2

# Run Ollama server
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

### Python Backend
```bash
# Activate venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:app --reload

# Run with specific port
uvicorn main:app --port 8000 --reload

# Run without auto-reload (production)
uvicorn main:app
```

### React Frontend
```bash
# Install dependencies
npm install

# Run development
npm start

# Build for production
npm run build

# Run tests
npm test
```

### Docker
```bash
# Build and run everything
docker-compose up --build

# Stop
docker-compose down

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

---

## 🐛 Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| "Cannot connect to localhost:11434" | Ollama not running | Run `ollama serve` |
| "Model not found: llama2" | Model not installed | Run `ollama pull llama2` |
| "No provider configured" | No .env file | Create .env with OLLAMA_BASE_URL |
| "Address already in use :8000" | Backend already running | Kill existing process or use different port |
| "Address already in use :3000" | Frontend already running | Kill existing process or use `PORT=3001 npm start` |
| Responses very slow | Model too large or on CPU | Use smaller model: `ollama pull mistral` |
| Out of memory | Insufficient RAM | Reduce model size or close other apps |

---

## 🏆 Models to Try

### Fast & Small (4GB)
```bash
ollama pull llama2          # Balanced
ollama pull mistral         # Good quality
ollama pull neural-chat     # Conversational
```

### Balanced (7-8GB)
```bash
ollama pull llama2:7b       # Original
ollama pull mistral:7b      # Better
```

### Best Quality (13GB+)
```bash
ollama pull llama2:13b      # Much better
ollama pull mistral:13b     # Excellent
ollama pull llama2:70b      # Best (40GB, needs GPU)
```

### Medical
```bash
ollama pull meditron        # Medical trained
ollama pull clinicalbert    # Clinical specific
```

---

## 🔍 Debug

### Check Backend is Running
```bash
curl http://localhost:8000/api/services
# Should return JSON list of services
```

### Check Ollama is Running
```bash
curl http://localhost:11434/api/tags
# Should return: {"models":[...]}
```

### Check Frontend is Running
```bash
curl http://localhost:3000
# Should return HTML page
```

### Test Agent Directly
```bash
cd backend
python -c "
from agents.clinic_agent import ClinicAgent
agent = ClinicAgent()
print(agent.get_greeting())
response = agent.process_message('I want to schedule an appointment', 'test-session')
print(response)
"
```

---

## 📁 Documentation

**Read in this order:**

1. **QUICK_REFERENCE.md** ← You are here
2. **OLLAMA_SETUP.md** - Detailed Ollama guide
3. **QUICK_START.md** - Full project quick start
4. **SETUP.md** - Comprehensive setup
5. **README.md** - Project overview

---

## 🌟 Key URLs

| Service | URL | Purpose |
|---------|-----|----------|
| Frontend | http://localhost:3000 | React UI |
| Backend API | http://localhost:8000 | FastAPI |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Ollama | http://localhost:11434 | LLM Server |

---

## 🚀 Status Check

**All services running?**

```bash
# In 4 different terminals:

# Terminal 1: Ollama
ollama serve
# Should show: Listening on 127.0.0.1:11434

# Terminal 2: Backend
cd backend && uvicorn main:app --reload
# Should show: Uvicorn running on http://127.0.0.1:8000

# Terminal 3: Frontend  
cd frontend && npm start
# Should show: webpack compiled successfully

# Terminal 4: Test
curl http://localhost:3000
curl http://localhost:8000/api/services
curl http://localhost:11434/api/tags
```

---

## 🔐 Environment Variables

**Full `.env` reference:**

```env
# === LLM PROVIDER (Choose ONE) ===
# Option 1: Ollama (Recommended - Free, Local)
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama2
OLLAMA_API_KEY=ollama

# Option 2: Groq (Free, Fast)
# GROQ_API_KEY=gsk-...
# GROQ_MODEL=llama-3.2-70b-versatile

# Option 3: OpenAI (Paid)
# OPENAI_API_KEY=sk-...

# === SPEECH-TO-TEXT (Optional) ===
# Only needed if you want automatic speech recognition
# OPENAI_API_KEY=sk-...

# === TEXT-TO-SPEECH (No key needed) ===
TTS_PROVIDER=gtts  # gtts or pyttsx3
TTS_LANGUAGE=en

# === SERVER CONFIG ===
HOST=0.0.0.0
PORT=8000
DEBUG=True
LOG_LEVEL=INFO

# === FRONTEND ===
FRONTEND_URL=http://localhost:3000

# === CLINIC INFO ===
CLINIC_NAME=My Clinic
CLINIC_PHONE=555-0100
```

---

## 🌟 Pro Tips

1. **Use tmux/screen for multiple terminals**
   ```bash
   tmux new-session -d -s ollama 'ollama serve'
   tmux new-session -d -s backend 'cd backend && uvicorn main:app --reload'
   tmux new-session -d -s frontend 'cd frontend && npm start'
   ```

2. **Monitor resource usage**
   ```bash
   # macOS
   top
   # Windows PowerShell
   Get-Process | Sort-Object CPU -Descending | Select-Object -First 5
   ```

3. **Test via curl**
   ```bash
   curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"user_message": "Hi", "session_id": "test"}'
   ```

4. **Enable GPU for Ollama**
   ```bash
   # Linux with NVIDIA
   apt install nvidia-cuda-toolkit
   ollama serve  # Auto-detects
   ```

---

**Ready to go! 🚀**

```bash
# Copy-paste this:
ollama serve  # Terminal 1
ollama pull llama2  # Terminal 2
cd backend && venv\Scripts\activate && uvicorn main:app --reload  # Terminal 3
cd frontend && npm start  # Terminal 4
# Then visit http://localhost:3000
```
