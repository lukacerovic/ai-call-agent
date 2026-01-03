# 🚀 START HERE - Quick Setup (15 Minutes)

**Don't know where to begin? Start here!**

---

## 📋 What This Project Does

An **AI-powered voice receptionist** for medical clinics:

```
 You call → AI answers → Books appointments → 24/7 automation
```

- 🎤 Voice-only interface (no typing needed)
- 🤖 AI runs **locally** on your computer (no cloud)
- 💰 **FREE** - no API costs
- 🔐 **Private** - everything stays on your machine

---

## ⚡ Absolute Quickest Setup (Copy-Paste)

If you've already installed **Ollama** and downloaded **llama2**, just run:

```bash
# Terminal 1
ollama serve

# Terminal 2
cd backend && venv\Scripts\Activate.ps1 && uvicorn main:app --reload

# Terminal 3
cd frontend && npm start

# Then visit: http://localhost:3000
```

Done! Skip to [Verify It Works](#verify-it-works) below.

---

## 🗑️ Full Setup (Never Done This Before?)

Read **COMPLETE_INSTALL.md** - it has everything step-by-step.

Or follow the summary below:

---

## 🗐 Quick Summary

### 1. Install Ollama

Download from: https://ollama.com/

Then in any terminal:
```bash
ollama serve

# You'll see: Listening on 127.0.0.1:11434
```

Leave that terminal running!

### 2. Download AI Model (In New Terminal)

```bash
ollama pull llama2

# Downloads 4GB model (~3-5 minutes)
# You'll see: "Pull complete"
```

### 3. Setup Python Backend (In New Terminal)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo OLLAMA_BASE_URL=http://localhost:11434/v1 > .env
echo OLLAMA_MODEL=llama2 >> .env
echo OLLAMA_API_KEY=ollama >> .env
echo TTS_PROVIDER=gtts >> .env

# Start backend
uvicorn main:app --reload

# You'll see: Clinic agent initialized
```

Leave that running!

### 4. Setup Frontend (In New Terminal)

```bash
cd frontend

# Install Node packages
npm install

# Start frontend
npm start

# Browser opens to http://localhost:3000
```

---

## ✅ Verify It Works

1. **Open browser** to http://localhost:3000
2. **Click** "📞 Call Clinic" button
3. **Allow** microphone when prompted
4. **Listen** to AI greeting
5. **Speak** naturally (e.g., "I want an appointment")
6. **AI responds** with next question

If you hear AI greeting = **Success!** ✅

---

## 📄 Documentation

### Read These (In Order)

1. **START_HERE.md** ← You are here
2. **COMPLETE_INSTALL.md** ← Full step-by-step guide
3. **QUICK_REFERENCE.md** ← Commands & troubleshooting
4. **OLLAMA_ONLY_SETUP.md** ← Ollama-specific help
5. **README.md** ← Project overview

---

## 🐛 Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|----------|
| "Can't connect to Ollama" | Make sure `ollama serve` is running |
| "Model not found" | Run `ollama pull llama2` |
| "Port already in use" | Kill the process or use different port |
| "npm install fails" | Run `npm install --legacy-peer-deps` |
| "No microphone access" | Check browser permissions |
| "Very slow responses" | Use `ollama pull mistral` instead |

**Still stuck?** Read COMPLETE_INSTALL.md "Troubleshooting" section.

---

## 🏆 System Requirements

- **OS**: Windows 10+, macOS, or Linux
- **RAM**: 8GB minimum (16GB better)
- **Storage**: 10GB free
- **Internet**: For initial setup only
- **API Keys**: **ZERO needed!**

---

## 📝 What You'll Need

### Download These

1. **Ollama** (free)
   - https://ollama.com/
   - ~150MB download

2. **Python** (free, usually already installed)
   - Windows: https://www.python.org/ (or use Windows Store)
   - macOS: brew install python3
   - Linux: apt install python3

3. **Node.js** (free)
   - https://nodejs.org/ (get LTS version)
   - ~100MB download

### Models (Auto-Downloaded)

```bash
ollama pull llama2      # 4GB
ollama pull mistral     # 4GB (faster alternative)
ollama pull llama3.2    # 8GB (better quality)
```

### Your Project

```bash
git clone https://github.com/lukacerovic/ai-call-agent.git
cd ai-call-agent
```

---

## 💄 What Each Component Does

### Frontend (React)
- What you see in browser
- Captures your voice via microphone
- Displays AI responses
- Real-time WebSocket connection

**Port**: http://localhost:3000

### Backend (FastAPI)
- Receives your voice data
- Talks to Ollama AI
- Converts text to speech
- Manages conversations

**Port**: http://localhost:8000

### Ollama (Local AI)
- Runs AI model locally
- No cloud, no API keys
- Understands patient needs
- Generates responses

**Port**: http://localhost:11434

---

## 🚀 Architecture

```
Your Computer:

┌──────────────────────────────────────┐
│ 📞 Your Voice                      │
│   ↓                              │
│ 👋 Browser :3000                 │
│ (React, TypeScript)              │
│   ↔️ WebSocket (real-time)         │
│ 🚀 Server :8000                 │
│ (FastAPI, Python)                │
│   ↔️ HTTP & Processes             │
│ 🤖 Ollama :11434                 │
│ (llama2, local AI)               │
│   ↓                              │
│ 💡 AI Response                   │
│   ↓                              │
│ 🔊 gTTS (text-to-speech)         │
│   ↓                              │
│ 🔈 Your Speakers                 │
│                                   │
└──────────────────────────────────────┘

✅ Everything local
✅ Everything offline (after setup)
✅ 100% private
✅ Zero API costs
```

---

## 📁 Key Information

### Ports (Don't Change These)
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000 
- **Ollama**: http://localhost:11434

### Configuration File
- **Location**: `backend/.env`
- **Only settings needed**:
  ```env
  OLLAMA_BASE_URL=http://localhost:11434/v1
  OLLAMA_MODEL=llama2
  OLLAMA_API_KEY=ollama
  TTS_PROVIDER=gtts
  ```

### Commands to Remember

```bash
# Ollama
ollama serve              # Start server
ollama pull llama2        # Download model
ollama list               # See installed models

# Python
python -m venv venv       # Create environment
venv\\Scripts\\Activate    # Activate (Windows)
source venv/bin/activate  # Activate (Mac/Linux)
pip install -r requirements.txt  # Install packages

# Node
npm install               # Install packages
npm start                 # Start dev server
```

---

## 🌟 Next Steps

1. **Just want to run it?**
   → Skip to [Absolute Quickest Setup](#absolute-quickest-setup-copy-paste) at top

2. **New to programming?**
   → Read COMPLETE_INSTALL.md (detailed steps)

3. **Already have Ollama?**
   → Jump to step 3 in [Full Setup](#full-setup-never-done-this-before)

4. **Having issues?**
   → Check [Troubleshooting](#troubleshooting-quick-fixes) section

5. **Want to customize?**
   → Edit `backend/data/services.json` or `.env` file

---

## 👏 Support

**Having trouble?** Here's what to do:

1. **Read the error message** - it usually says what's wrong
2. **Check relevant documentation**:
   - Ollama issues → OLLAMA_ONLY_SETUP.md
   - Setup issues → COMPLETE_INSTALL.md
   - Commands → QUICK_REFERENCE.md
3. **Google the error** - most Python/Node errors are common
4. **Check GitHub issues** - others might have same problem

---

## 🎉 When You're Done

You'll have a working medical clinic AI that:

- 📞 Answers phones 24/7
- 📅 Books appointments
- 🤖 Understands patient needs
- 🔐 Keeps data private
- 💰 Costs zero dollars

---

## 🚀 Ready to Start?

### Option 1: I know what I'm doing
→ Go to [Absolute Quickest Setup](#absolute-quickest-setup-copy-paste)

### Option 2: I need detailed steps
→ Open COMPLETE_INSTALL.md

### Option 3: I'm looking for specific help
→ Check [Troubleshooting](#troubleshooting-quick-fixes) or QUICK_REFERENCE.md

---

**Let's build your AI clinic!** 🃞🤖🚀
