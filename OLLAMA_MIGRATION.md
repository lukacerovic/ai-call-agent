# ✅ Ollama Support - Fixed the API Key Issue!

## 💅 The Problem You Had

You got this error:
```
ValueError: OpenAI API key not found. Set OPENAI_API_KEY environment variable.
```

Because the old code **required** an OpenAI API key, even though you wanted to use Ollama.

---

## 🚀 The Solution

I've updated the backend to work **exactly like your AI_Court project**:

### Before (Broken)
```python
# old stt.py
if not api_key:
    raise ValueError("OpenAI API key not found!")  # ❌ Crashes!
```

### After (Fixed)
```python
# new clinic_agent.py
if self.provider == "ollama":
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    api_key = os.getenv("OLLAMA_API_KEY", "ollama")
    return OpenAI(base_url=base_url, api_key=api_key)  # ✅ Works!
```

---

## 📁 What Changed

### 1. **clinic_agent.py** - Provider Auto-Detection

Now supports 3 LLM providers (checks in order):

```
OLLAMA_BASE_URL set?
    ✓ YES → Use Ollama (local, free)
    ✗ NO
        ↓
    GROQ_API_KEY set?
        ✓ YES → Use Groq (fast, free tier)
        ✗ NO
            ↓
        OPENAI_API_KEY set?
            ✓ YES → Use OpenAI (paid)
            ✗ NO → Error with helpful message
```

**Code:**
```python
def _determine_provider(self) -> str:
    if os.getenv("OLLAMA_BASE_URL"):
        return "ollama"
    elif os.getenv("GROQ_API_KEY"):
        return "groq"
    elif os.getenv("OPENAI_API_KEY"):
        return "openai"
    else:
        raise ValueError("Set OLLAMA_BASE_URL, GROQ_API_KEY, or OPENAI_API_KEY")
```

### 2. **stt.py** - Optional Speech-to-Text

Old version:
```python
if not api_key:
    raise ValueError(...)  # ❌ Always crashes
```

New version:
```python
if not api_key:
    logger.warning("STT not available")  # ✅ Just warns
    self.is_available = False
    return  # Continue anyway
```

### 3. **.env.example** - New Configuration

Shows all three options:

```env
# Option 1: Ollama (Recommended - FREE & LOCAL)
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama2
OLLAMA_API_KEY=ollama

# Option 2: Groq (FREE - fast, needs API key)
GROQ_API_KEY=gsk-your-key-here
GROQ_MODEL=llama-3.2-70b-versatile

# Option 3: OpenAI (PAID - needs API key)
OPENAI_API_KEY=sk-your-key-here
```

---

## 🤞 How to Use (Your Setup)

Your setup is exactly like AI_Court:

### Step 1: Install & Run Ollama

```bash
# 1. Download from https://ollama.com/
# 2. Install
# 3. Run:
ollama serve

# In another terminal:
ollama pull llama2
```

### Step 2: Configure Backend

**Edit `backend/.env`:**

```env
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama2
OLLAMA_API_KEY=ollama
TTS_PROVIDER=gtts
```

**That's it!** No OpenAI key needed.

### Step 3: Start Backend

```bash
cd backend
venv\Scripts\activate  # Windows
uvicorn main:app --reload
```

✅ Should work now without errors!

---

## 👓 Comparison: Your AI_Court vs Our AI Call Agent

### AI_Court Setup
```python
from openai import OpenAI

# Your code:
OLLAMA_LOCALHOST = "http://localhost:11434/v1"
OLLAMA_MODEL = "llama3.2"
ollama_client = OpenAI(base_url=OLLAMA_LOCALHOST, api_key="ollama")
```

### AI Call Agent Setup (Now)
```python
from openai import OpenAI

# Our code (automatic):
if self.provider == "ollama":
    base_url = os.getenv("OLLAMA_BASE_URL")  # User sets in .env
    api_key = os.getenv("OLLAMA_API_KEY", "ollama")
    return OpenAI(base_url=base_url, api_key=api_key)
```

**Same pattern, but configurable and error-safe!** 🎉

---

## 🕺 Troubleshooting

### Error: "Cannot connect to http://localhost:11434/v1"

**Fix**: Make sure Ollama is running:
```bash
ollama serve
```

You should see: `Listening on 127.0.0.1:11434`

### Error: "Model 'llama2' not found"

**Fix**: Pull the model:
```bash
ollama pull llama2
```

### Error: "No provider configured"

**Fix**: Set one of these in `.env`:
- `OLLAMA_BASE_URL=http://localhost:11434/v1` (Recommended)
- `GROQ_API_KEY=gsk-...` (Alternative)
- `OPENAI_API_KEY=sk-...` (Last resort)

### Responses are slow

**Fix**: Use a smaller model:
```bash
ollama pull mistral  # Faster, 4GB
ollama pull neural-chat  # Good balance
```

Then update `.env`:
```env
OLLAMA_MODEL=mistral
```

---

## 🏆 Model Selection

### Fastest (4GB)
- `llama2` - Balanced
- `mistral` - Good quality
- `neural-chat` - Conversational

### Balanced (7-8GB)
- `llama2:7b` - Original
- `mistral:7b` - Better quality

### Best Quality (13GB+)
- `llama2:13b` - Much better
- `mistral:13b` - Excellent
- `llama2:70b` - Best (needs GPU, 40GB)

For medical context, try:
- `meditron` - Trained on medical data
- `clinicalbert` - Medical specific

---

## 🔌 Files Updated

| File | Change |
|------|--------|
| `backend/agents/clinic_agent.py` | Added provider auto-detection |
| `backend/audio/stt.py` | Made OpenAI optional |
| `backend/.env.example` | Added Ollama configuration |
| `OLLAMA_SETUP.md` | New complete guide |
| `OLLAMA_MIGRATION.md` | This file |

---

## ✅ Verification

To verify everything works:

```bash
# 1. Check Ollama is running
curl http://localhost:11434/api/tags
# Should return: {"models":[{"name":"llama2:latest",...}]}

# 2. Check backend can connect
cd backend
python -c "from agents.clinic_agent import ClinicAgent; agent = ClinicAgent(); print('Connected!')"
# Should print: Connected!

# 3. Start the app
uvicorn main:app --reload
# Should work without OpenAI key errors!
```

---

## 📁 Documentation

Read these in order:

1. **OLLAMA_SETUP.md** - Complete Ollama setup guide (5-minute quickstart)
2. **OLLAMA_MIGRATION.md** - This file (explanation of changes)
3. **QUICK_START.md** - Full quick start (if using Groq/OpenAI)
4. **SETUP.md** - Detailed setup guide

---

## 🚀 Next Steps

1. Read `OLLAMA_SETUP.md`
2. Install Ollama from https://ollama.com/
3. Run `ollama serve`
4. Pull a model: `ollama pull llama2`
5. Set up `.env` with `OLLAMA_BASE_URL=http://localhost:11434/v1`
6. Run backend: `uvicorn main:app --reload`
7. It should work now! 🎉

---

**Your AI Call Agent now works locally, just like AI_Court, with no API keys!**

👀 Welcome to the club! 👏
