# 🐳 Windows Python Issue - SOLUTION

## The Problem

You're getting this error:

```
ERROR: Could not find a version that satisfies the requirement audio-to-text-api==1.0.1
ERROR: Could not find a version that satisfies the requirement pyannote.audio==2.1.1
```

And version conflicts like:

```
ERROR: Ignored the following versions that require a different python version: 
1.16.0 Requires-Python >=3.11
```

## Why This Happens

1. **Python Version Mismatch**: You likely have Python 3.12+, but we need 3.10 or 3.11
2. **Package Issues**: Some packages we initially included don't exist or have conflicts
3. **Windows-Specific**: Windows sometimes has issues with compiled packages

## ✅ THE FIX

### Step 1: Check Your Python Version

```bash
python --version
```

You should see: `Python 3.10.x` or `Python 3.11.x`

If you see `3.12.x` or higher → Continue to Step 2

### Step 2: Install Python 3.11 (If Needed)

#### Option A: Python.org (Recommended)

1. Go to https://www.python.org/downloads/release/python-3113/
2. Download "Windows installer (64-bit)" or "Windows installer (32-bit)"
3. **IMPORTANT**: Check "Add Python to PATH" during installation
4. Click "Install Now"
5. Open new Command Prompt or PowerShell

#### Option B: Chocolatey (Windows Package Manager)

```bash
choco install python311
```

#### Option C: Windows Store

- Search "Python 3.11" in Microsoft Store
- Click Install

### Step 3: Update Your Project

**Delete old venv:**

```bash
cd ai-call-agent/backend
rmdir /s venv  # Windows
# or rm -r venv  # PowerShell
```

**Download updated requirements.txt:**

Just run:
```bash
git pull origin main
```

This gets the fixed requirements.txt without the problematic packages.

### Step 4: Fresh Setup

**Windows Command Prompt:**

```bash
cd ai-call-agent\backend
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Windows PowerShell:**

```powershell
cd ai-call-agent\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell complains about script execution:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

## 📝 What We Fixed

Old problematic `requirements.txt` had:
```
pyaudio==0.2.13           # ❌ Doesn't work well on Windows
pyannote.audio==2.1.1     # ❌ Complex dependencies
audio-to-text-api==1.0.1  # ❌ Doesn't exist
```

New version uses:
```
# ✅ OpenAI Whisper (built-in via openai library)
# ✅ gTTS or pyttsx3 for Text-to-Speech
# ✅ No problematic compiled packages
```

## 💡 Why These Changes?

1. **gTTS** - Pure Python, no compilation needed, works on Windows
2. **pyttsx3** - Offline TTS using system voices, very reliable
3. **Removed pyannote** - Our energy-based VAD works fine
4. **Removed audio-to-text-api** - Using OpenAI Whisper instead

## 🏧 If It Still Doesn't Work

### Issue: "Python not found"

```bash
# Check Python is in PATH
python --version

# If not, add to PATH:
# Windows: Environment Variables → Edit → Add Python installation directory
```

### Issue: "pip install fails"

```bash
# Try with Python directly
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Issue: "venv not working"

```bash
# Use alternative venv tool
python -m venv venv --upgrade-deps
```

### Issue: "Port 8000 already in use"

```bash
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F

# Or use different port
uvicorn main:app --port 8001
```

## 🚄 Alternative: Use Docker

Avoid all Python setup issues with Docker:

```bash
docker-compose up --build
```

Everything runs in containers (no system Python needed).

## ✨ Verify Installation

```bash
# Activate venv
venv\Scripts\activate  # Windows

# Test imports
python -c "import fastapi; print('FastAPI OK')"
python -c "import openai; print('OpenAI OK')"
python -c "import gtts; print('gTTS OK')"

# All should print OK
```

## 🐛 Still Having Issues?

1. **Take a screenshot** of the exact error
2. **Open an issue** on GitHub with:
   - Your Python version: `python --version`
   - Your Windows version: `ver`
   - The error message (full stack trace)
3. **Tag it**: `[Windows] [Help]`

## 🎉 Success Checklist

- ✅ Python 3.10 or 3.11 installed
- ✅ venv activated (you see `(venv)` in command prompt)
- ✅ `pip install -r requirements.txt` completes without errors
- ✅ `python -c "import fastapi"` works
- ✅ `uvicorn main:app --reload` starts without errors
- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on http://localhost:3000
- ✅ Browser can call the clinic

---

**You're now ready! Follow QUICK_START.md next. 🚀**
