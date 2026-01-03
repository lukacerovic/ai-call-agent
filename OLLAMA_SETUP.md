# 🗿 Ollama Local Setup - No API Key Needed

This guide shows how to run AI Call Agent **completely locally** using Ollama, just like your AI_Court project.

**No API keys required. No costs. Everything runs on your computer.**

---

## 🚀 Quick Start (5 minutes)

### Step 1: Install Ollama

**Windows/macOS:**
- Go to https://ollama.com/
- Download and install
- Open and let it run in background

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Step 2: Pull a Model

**Open Terminal/PowerShell and run:**

```bash
ollama pull llama2
```

This downloads the LLaMA 2 model (~4GB). Takes a few minutes first time.

### Step 3: Start Ollama Server

```bash
ollama serve
```

✅ You should see: `Listening on 127.0.0.1:11434`

**Leave this running in background.**

### Step 4: Configure Your Backend

Edit `backend/.env`:

```env
# Use Ollama (no API key needed!)
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama2
OLLAMA_API_KEY=ollama

# TTS (Text-to-Speech) - doesn't need API key
TTS_PROVIDER=gtts

# But STT (Speech-to-Text) needs OpenAI
# For testing without STT, leave OPENAI_API_KEY blank
# Frontend will send raw audio to backend
```

### Step 5: Run Backend

```bash
cd backend
venv\Scripts\activate  # Windows
uvicorn main:app --reload
```

✅ Should see: `Uvicorn running on http://127.0.0.1:8000`

### Step 6: Run Frontend

**New terminal:**

```bash
cd frontend
npm start
```

### Step 7: Call the Clinic

1. Browser opens http://localhost:3000
2. Click "📞 Call Clinic"
3. Allow microphone
4. Listen to AI greeting (powered by Ollama!)
5. Speak and chat

---

## 👐 Available Models

### Fast & Small (Recommended for Testing)

```bash
ollama pull llama2        # ~4GB, fast, good quality
ollama pull mistral       # ~4GB, slightly better quality
ollama pull neural-chat   # ~4GB, optimized for chat
```

### Larger & Better Quality

```bash
ollama pull llama2:13b    # ~8GB, better quality
ollama pull mistral:7b    # ~5GB
ollama pull llama2:70b    # ~40GB, best quality (needs GPU)
```

### Medical/Specialized

```bash
ollama pull meditron      # Trained for medical domain
ollama pull clinicalbert  # Medical-specific model
```

After pulling, update `.env`:
```env
OLLAMA_MODEL=model_name
```

---

## 📊 Full Configuration

**`backend/.env` for Ollama-only setup:**

```env
# === LOCAL LLM ===
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama2
OLLAMA_API_KEY=ollama

# === TEXT-TO-SPEECH (No API needed) ===
TTS_PROVIDER=gtts
TTS_LANGUAGE=en

# === SPEECH-TO-TEXT (Optional - needs OpenAI key if used) ===
# Leave blank to skip STT
OPENAI_API_KEY=

# === SERVER ===
HOST=0.0.0.0
PORT=8000
DEBUG=True
LOG_LEVEL=INFO

# === CLINIC INFO ===
CLINIC_NAME=Local AI Clinic
CLINIC_PHONE=555-0100
```

---

## 🐛 Troubleshooting Ollama

### ❌ "Connection refused" error

```
Error: Cannot connect to http://localhost:11434/v1
```

**Solution**: Make sure Ollama server is running:

```bash
ollama serve
```

### ❌ "Model not found" error

```
Error: model 'llama2' not found
```

**Solution**: Pull the model:

```bash
ollama pull llama2
```

### ❌ Responses are very slow

**Cause**: Model is too large or running on CPU only

**Solutions**:
1. Use smaller model: `ollama pull mistral` (4GB instead of 7GB)
2. Enable GPU support:
   - **NVIDIA**: Install CUDA Toolkit (Ollama auto-detects)
   - **AMD**: Install ROCm
   - **Mac**: Already uses GPU by default

### ❌ Out of memory error

**Solution**: Reduce model size or free up RAM

```bash
# Check installed models
ollama list

# Remove large models
ollama rm llama2:13b

# Use smaller model
ollama pull neural-chat  # Only 4GB
```

### ❌ Model takes too long to start

**First run**: Normal, model is loading (~30 seconds)
**Subsequent runs**: Should be instant

---

## ⚡ Performance Tips

### Enable GPU Acceleration

**NVIDIA GPUs:**
```bash
# Install CUDA: https://developer.nvidia.com/cuda-downloads
# Ollama auto-detects
ollama serve
```

**AMD GPUs:**
```bash
# Install ROCm, then
OLLAMA_NUM_THREAD=4 ollama serve
```

**Apple Silicon (M1/M2/M3):**
```bash
# Already optimized, runs on GPU automatically
ollama serve
```

### Optimize Model Size

**For 8GB RAM:**
```bash
ollama pull mistral      # 4GB, fast
ollama pull neural-chat  # 4GB, good quality
```

**For 16GB RAM:**
```bash
ollama pull llama2:13b   # 8GB, better
ollama pull mistral:7b   # 5GB
```

**For 32GB+ RAM:**
```bash
ollama pull llama2:70b   # 40GB, best (needs GPU)
```

### Tune Response Time

**In `backend/.env`:**

```env
# Reduce token length for faster responses
max_tokens=100  # Default: 150

# Increase for more detailed responses
max_tokens=200

# Lower temperature for consistent responses
temperature=0.5  # Default: 0.7
```

---

## 📄 Architecture (Your Setup)

```
Your Computer:
┌────────────────────────────────────────────────────────┐
│                                                                    │
│  ┌──────────────────┌──────────────────┐
│  │   React Frontend   │◄─────────────→ FastAPI Backend   │
│  │   (Port 3000)      │   WebSocket (8000)  │
│  └──────────────────└──────────────────┘
│         │                                 │
│         │ Microphone input              │ Ollama LLM
│         │ Audio processing              │ (Port 11434)
│         └────────────────────────────────────────→ gTTS for TTS
│                                                   │
└────────────────────────────────────────────────────────┘

❌ NO CLOUD SERVICES
❌ NO API KEYS NEEDED
❌ NO INTERNET REQUIRED (after initial model download)
❌ 100% PRIVACY - Everything runs locally
```

---

## 📁 Comparing Providers

| Feature | Ollama | Groq | OpenAI |
|---------|--------|------|--------|
| **Cost** | Free | Free (tier) | Paid |
| **Speed** | Medium | Fast | Fast |
| **Quality** | Good | Excellent | Excellent |
| **API Key** | ❌ No | ✅ Yes | ✅ Yes |
| **Privacy** | ✅ Local | ❌ Cloud | ❌ Cloud |
| **Internet** | ❌ Needed once | ✅ Always | ✅ Always |
| **Setup** | ✅ Easy | Medium | Easy |

---

## 🚀 Next Steps

1. **Install Ollama**: https://ollama.com/
2. **Run**: `ollama serve`
3. **Pull model**: `ollama pull llama2`
4. **Configure**: Edit `backend/.env` (see above)
5. **Start backend**: `uvicorn main:app --reload`
6. **Start frontend**: `npm start`
7. **Call the clinic!**

---

## 🐛 Still Need Help?

Compare with your AI_Court project setup:

```python
# Your AI_Court setup (same approach!)
from openai import OpenAI

OLLAMA_LOCALHOST = "http://localhost:11434/v1"
ollama_client = OpenAI(base_url=OLLAMA_LOCALHOST, api_key="ollama")

# Now ours works the same way automatically!
```

The backend now auto-detects and uses Ollama just like your project.

---

**Enjoy your local AI clinic! 🎉**

*No costs, no worries about API limits, everything runs on your machine.*
