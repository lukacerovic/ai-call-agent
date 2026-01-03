# 🚀 Complete Installation & Setup Guide - Llama3.2 + AI Call Agent

**Everything you need from zero to running AI clinic!**

Estimated time: **30 minutes** (including model download)

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Install Ollama](#install-ollama)
3. [Download Llama3.2](#download-llama32)
4. [Install Project](#install-project)
5. [Run Everything](#run-everything)
6. [Verify It Works](#verify-it-works)
7. [Troubleshooting](#troubleshooting)

---

## 💻 System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **OS** | Windows 10+, macOS 10.13+, Linux |
| **RAM** | 8GB minimum (16GB recommended) |
| **Storage** | 10GB free (for models) |
| **CPU** | Any modern processor |
| **GPU** | Optional (speeds up inference) |
| **Internet** | For initial setup only |

### Check Your RAM

**Windows PowerShell:**
```powershell
Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory
# Divide result by 1GB to get GB count
```

**Mac/Linux:**
```bash
free -h  # Linux
vm_stat  # Mac
```

### Optional: GPU Support

**NVIDIA (CUDA):**
- Download: https://developer.nvidia.com/cuda-downloads
- Ollama auto-detects

**AMD (ROCm):**
- Download: https://rocmdocs.amd.com/en/docs-5.2.0/deploy/linux/index.html

**Apple Silicon (M1/M2/M3):**
- Already optimized, runs on GPU automatically

---

## 🗿 Step 1: Install Ollama

### Windows

1. **Download Ollama**
   - Go to: https://ollama.com/
   - Click "Download for Windows"
   - Run the installer (OllamaSetup.exe)

2. **Install**
   - Follow the installer wizard
   - Click "Next" through all dialogs
   - Click "Install"
   - Wait for installation to complete

3. **Verify Installation**
   - Open PowerShell
   - Run:
   ```powershell
   ollama --version
   # Output: ollama version X.X.X
   ```

### macOS

1. **Download Ollama**
   - Go to: https://ollama.com/
   - Click "Download for macOS"
   - Two versions available:
     - **Intel Macs**: Download Intel version
     - **Apple Silicon (M1/M2/M3)**: Download Apple Silicon version

2. **Install**
   - Double-click the downloaded DMG file
   - Drag "Ollama" to Applications folder
   - Wait for copy to complete

3. **Verify**
   ```bash
   ollama --version
   # Output: ollama version X.X.X
   ```

### Linux

**Ubuntu/Debian:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh

# Verify
ollama --version
```

**Other Distributions:**
See: https://github.com/ollama/ollama/blob/main/README.md

---

## 💾 Step 2: Download Llama3.2

### Start Ollama Server

Ollama server must be running before you can download models.

**Windows (PowerShell):**
```powershell
ollama serve

# You'll see:
# Listening on 127.0.0.1:11434
# Leave this window open!
```

**macOS/Linux (Terminal):**
```bash
ollama serve

# You'll see:
# Listening on 127.0.0.1:11434
# Leave this terminal open!
```

### Download Llama3.2 Model

Open a **NEW** terminal/PowerShell window and run:

```bash
ollama pull llama2
```

**Note**: We'll use `llama2` because `llama3.2` requires more resources. If you want the latest, use:

```bash
# For better quality (requires 8GB+ RAM)
ollama pull llama3.2

# Or faster version (requires 16GB+ RAM)
ollama pull llama3.2:13b
```

### Download Progress

```
Pulling manifest
Pulling d8e0cf3c
[==========================>] 3.8 GB / 3.8 GB

Pull complete
Total duration: 5m30s
```

**Time to download:**
- llama2 (4GB): ~3-5 minutes
- llama3.2 (8GB): ~6-10 minutes  
- llama3.2:13b (13GB): ~10-15 minutes

### Verify Download

Run this command to see installed models:

```bash
ollama list

# Output:
# NAME            ID              SIZE    MODIFIED
# llama2:latest   <hash>          3.8 GB  2 minutes ago
```

✅ **Model is ready!**

---

## 📋 Step 3: Install Python Project

### 3a. Get the Project

**Option 1: Already have the repo?**
```bash
cd path/to/ai-call-agent
```

**Option 2: Clone fresh?**
```bash
git clone https://github.com/lukacerovic/ai-call-agent.git
cd ai-call-agent
```

### 3b. Setup Backend

#### Create Virtual Environment

**Windows (PowerShell):**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1

# You should see: (venv) in your prompt
```

**macOS/Linux (Terminal):**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate

# You should see: (venv) in your prompt
```

#### Install Python Dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# This installs:
# - fastapi (web framework)
# - uvicorn (server)
# - websockets (real-time communication)
# - openai (for Ollama connection)
# - gtts (text-to-speech)
# - And more...

# Should take ~2-3 minutes
```

#### Create .env File

**Windows (PowerShell):**
```powershell
$env_content = @"
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama2
OLLAMA_API_KEY=ollama
TTS_PROVIDER=gtts
PORT=8000
DEBUG=True
LOG_LEVEL=INFO
CLINIC_NAME=Local Medical Clinic
CLINIC_PHONE=555-0100
"@

$env_content | Set-Content .env
```

**macOS/Linux (Terminal):**
```bash
cat > .env << 'EOF'
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama2
OLLAMA_API_KEY=ollama
TTS_PROVIDER=gtts
PORT=8000
DEBUG=True
LOG_LEVEL=INFO
CLINIC_NAME=Local Medical Clinic
CLINIC_PHONE=555-0100
EOF
```

**Or manually:**
Create file `backend/.env` with this content:
```env
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama2
OLLAMA_API_KEY=ollama
TTS_PROVIDER=gtts
PORT=8000
DEBUG=True
LOG_LEVEL=INFO
CLINIC_NAME=Local Medical Clinic
CLINIC_PHONE=555-0100
```

### 3c. Setup Frontend

**Open NEW terminal (keep backend terminal open)**

```bash
cd frontend

# Install Node.js dependencies
npm install

# This installs:
# - React (UI framework)
# - TypeScript (type safety)
# - Web Audio API
# - And more...

# Should take ~2-3 minutes
```

---

## 🚀 Step 4: Run Everything

You'll need **4 terminal windows** open simultaneously:

### Terminal 1: Ollama Server

```bash
ollama serve

# Output:
# Listening on 127.0.0.1:11434

# Keep this running!
```

### Terminal 2: Backend API

```bash
# Make sure you're in backend folder
cd backend

# Activate venv (if not already active)
venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate  # macOS/Linux

# Start server
uvicorn main:app --reload

# Output:
# ✅ Clinic agent initialized
# ✅ System ready to receive calls
# INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Terminal 3: Frontend

```bash
# Make sure you're in frontend folder
cd frontend

# Start development server
npm start

# Output:
# Compiled successfully!
# You can now view the app in your browser.
# Local:            http://localhost:3000

# Browser should open automatically
```

### Terminal 4: Testing (Optional)

```bash
# Verify all services are running
curl http://localhost:8000/health
curl http://localhost:11434/api/tags
curl http://localhost:3000

# All should return success
```

---

## ✅ Step 5: Verify It Works

### Check All Services

**Ollama Server:**
```bash
curl http://localhost:11434/api/tags

# Expected output:
# {"models":[{"name":"llama2:latest",...}]}
```

**Backend API:**
```bash
curl http://localhost:8000/health

# Expected output:
# {"status":"healthy","timestamp":"2026-01-03T..."}
```

**Backend Services:**
```bash
curl http://localhost:8000/services

# Expected output:
# {"success":true,"services":[...]}
```

**Frontend:**
Open browser to http://localhost:3000
- Should see: "Call Clinic" button
- Should see: Animated phone icon

### Test Voice Call

1. **Allow Microphone**
   - Click "Call Clinic"
   - Browser asks for microphone access
   - Click "Allow"

2. **Listen to AI Greeting**
   - You should hear the AI greeting
   - Text will appear in console

3. **Speak**
   - Say something like: "I want to schedule an appointment"
   - AI should respond

4. **Check Logs**
   - Backend terminal shows: `🎤 Agent: [response]`
   - Ollama terminal shows processing

✅ **Everything working!**

---

## 📊 Step 6: Project Structure

```
ai-call-agent/
├── backend/                    # Python FastAPI server
│   ├── main.py                # FastAPI app entry point
│   ├── agents/                # AI agent logic
│   │   └── clinic_agent.py   # Medical receptionist AI
│   ├── audio/                 # Audio processing
│   │   ├── stt.py            # Speech-to-Text (optional)
│   │   ├── tts.py            # Text-to-Speech (gTTS)
│   │   └── vad.py            # Voice Activity Detection
│   ├── data/                  # Static data
│   │   ├── services.json     # Medical services
│   │   └── reservations.json # Bookings
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Configuration (you created this)
│   └── venv/                  # Virtual environment
│
├── frontend/                   # React TypeScript app
│   ├── src/
│   │   ├── components/       # React components
│   │   │   └── CallInterface.tsx
│   │   ├── styles/           # CSS styles
│   │   ├── App.tsx           # Main app
│   │   └── index.tsx         # Entry point
│   ├── package.json          # Node.js dependencies
│   └── node_modules/         # Installed packages
│
├── README.md                   # Project overview
├── COMPLETE_INSTALL.md         # This file
├── OLLAMA_ONLY_SETUP.md        # Ollama setup
├── QUICK_REFERENCE.md          # Commands reference
└── .gitignore                  # Git ignore rules
```

---

## 🐛 Troubleshooting

### Problem: "Listening on port 11434" but can't connect

**Solution:**
```bash
# Make sure Ollama server is fully started
# Wait 5 seconds
# Try again

# Or check if another app is using port 11434
netstat -ano | findstr :11434  # Windows
lsof -i :11434                  # macOS/Linux
```

### Problem: "Model not found: llama2"

**Solution:**
Pull the model again:
```bash
ollama pull llama2

# Verify
ollama list
```

### Problem: "Cannot find module 'xyz'"

**Solution:**
Reinst all dependencies:
```bash
cd backend
rm -rf venv  # Remove old venv
python -m venv venv  # Create new
venv\Scripts\Activate.ps1  # Activate
pip install -r requirements.txt  # Reinstall
```

### Problem: "Address already in use :8000"

**Solution:**
Kill the process using port 8000:

**Windows:**
```powershell
# Find process
netstat -ano | findstr :8000

# Kill it (replace XXXXX with PID)
taskkill /PID XXXXX /F
```

**macOS/Linux:**
```bash
lsof -i :8000
kill -9 XXXXX
```

### Problem: "Response is very slow"

**Causes:**
- Model is large
- Running on CPU only
- Low RAM available

**Solutions:**
1. Use smaller model:
```bash
ollama pull mistral  # 4GB, faster
```

Update .env:
```env
OLLAMA_MODEL=mistral
```

2. Enable GPU (NVIDIA):
```bash
# Install CUDA
# Ollama auto-detects
```

3. Close other apps to free RAM

### Problem: "Out of memory"

**Solution:**
```bash
# Check RAM
free -h  # Linux

# Use smaller model
ollama rm llama2:13b  # Remove large
ollama pull mistral    # Install small
```

### Problem: npm start fails

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

### Problem: "CORS error" in browser console

**Solution:**
Make sure backend is running on port 8000:
```bash
cd backend
uvicorn main:app --reload --port 8000
```

---

## 📁 Quick Reference Commands

### Ollama Commands
```bash
# List models
ollama list

# Download model
ollama pull llama2

# Remove model
ollama rm llama2

# Run server
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

### Backend Commands
```bash
# Activate venv (Windows)
venv\Scripts\Activate.ps1

# Activate venv (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload

# Deactivate venv
deactivate
```

### Frontend Commands
```bash
# Install dependencies
npm install

# Run development server
npm start

# Build for production
npm run build

# Test
npm test
```

### Port Checking
```bash
# Windows
netstat -ano | findstr :<PORT>

# macOS/Linux
lsof -i :<PORT>
```

---

## 📑 Configuration Reference

### .env File Explanation

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434/v1  # Ollama server URL
OLLAMA_MODEL=llama2                        # Model to use
OLLAMA_API_KEY=ollama                      # Local key (always "ollama")

# Text-to-Speech
TTS_PROVIDER=gtts                          # Use Google TTS (free)
TTS_LANGUAGE=en                            # Language

# Server
PORT=8000                                  # Backend port
HOST=0.0.0.0                              # Listen on all interfaces
DEBUG=True                                 # Enable debug mode
LOG_LEVEL=INFO                             # Logging level

# Clinic Information
CLINIC_NAME=Local Medical Clinic           # Your clinic name
CLINIC_PHONE=555-0100                     # Contact number
EMERGENCY_HOTLINE=911                     # Emergency number

# Optional: For production
# DEBUG=False
# LOG_LEVEL=WARNING
```

---

## 🌟 Model Comparison

| Model | Size | Speed | Quality | Command |
|-------|------|-------|---------|----------|
| llama2 | 4GB | Fast | Good | `ollama pull llama2` |
| mistral | 4GB | Fast | Good | `ollama pull mistral` |
| neural-chat | 4GB | Fast | Good | `ollama pull neural-chat` |
| llama3.2 | 8GB | Medium | Great | `ollama pull llama3.2` |
| llama2:13b | 8GB | Slow | Better | `ollama pull llama2:13b` |
| llama3.2:13b | 13GB | Slow | Better | `ollama pull llama3.2:13b` |

**Recommended**: `llama2` or `mistral` for best balance

---

## 🌟 Next Steps

1. ✅ Install Ollama
2. ✅ Download llama2 model
3. ✅ Run Ollama server
4. ✅ Setup Python backend
5. ✅ Setup Node.js frontend
6. ✅ Run all services (4 terminals)
7. ✅ Visit http://localhost:3000
8. ✅ Click "Call Clinic"
9. ✅ Start chatting!

---

## ✅ Success Checklist

```
[ ] Ollama installed
[ ] llama2 model downloaded (ollama list shows it)
[ ] Ollama server running (listening on 127.0.0.1:11434)
[ ] Python venv created and activated
[ ] requirements.txt installed (pip install -r requirements.txt)
[ ] .env file created in backend folder
[ ] Backend running (uvicorn shows "Clinic agent initialized")
[ ] npm install completed in frontend
[ ] Frontend running (npm start shows "Compiled successfully")
[ ] Browser opens to http://localhost:3000
[ ] "Call Clinic" button visible
[ ] Microphone permission allowed
[ ] AI greeting heard
[ ] Can speak and get responses
```

If all checked: **You're done! Your AI clinic is running!** 🎉

---

## 📀 Getting Help

If you run into issues:

1. **Check logs**
   - Look at terminal output
   - Check browser console (F12)

2. **Read documentation**
   - OLLAMA_ONLY_SETUP.md
   - QUICK_REFERENCE.md
   - README.md

3. **Common fixes**
   - Make sure all 4 services are running
   - Check ports are not in use
   - Verify model is downloaded
   - Clear browser cache (Ctrl+Shift+Delete)

4. **Still stuck?**
   - Check GitHub issues
   - Create new issue with logs

---

**You're all set! Welcome to your AI-powered medical clinic!** 📞

**Happy chatting!** 😊
