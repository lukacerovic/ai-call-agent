# 🔊 Fix Audio Issues - No Sound from AI

**Problem**: You don't hear the AI greeting or responses

---

## 🐛 Issue 1: gTTS Error (Fixed!)

### Error Message
```
2026-01-03 12:57:23,681 - audio.tts - ERROR - gTTS error: Failed to connect. Probable cause: Unknown
```

### What Was Wrong
- gTTS (Google Text-to-Speech) needs **internet connection**
- It was trying to connect to Google servers
- Connection failed = no audio

### What I Fixed
- Changed default from **gTTS to pyttsx3**
- pyttsx3 is **completely offline** (uses system voices)
- No internet needed!

### Files Updated
1. `backend/audio/tts.py` - Default to pyttsx3
2. `backend/.env` - Changed `TTS_PROVIDER=pyttsx3`

---

## 🔂 Issue 2: Backend Restarting

**You MUST restart the backend** for the TTS fix to take effect:

```bash
# In backend terminal:
# 1. Stop the server: Press Ctrl+C

# 2. Restart it:
uvicorn main:app --reload

# You should see:
# 2026-01-03 ... - audio.tts - INFO - ✅ TTS initialized with provider: pyttsx3 (local, works offline)
# ✅ Clinic agent initialized
```

---

## 🔈 Issue 3: No Audio Coming Through Browser

If you restart backend but **still no sound**, the issue is **frontend to backend connection**.

### Check Backend is Sending Audio

**You should see in backend terminal:**
```
2026-01-03 12:57:23,651 - main - INFO - 📞 New call connected
2026-01-03 12:57:23,651 - main - INFO - 🎤 Agent: Hello, thank you for calling...
```

If you see this = **Backend is working correctly** ✅

### Check Frontend is Receiving Audio

1. **Open browser DevTools**: Press `F12`
2. **Go to Console tab**
3. **Look for errors** (red text)
4. **Common errors:**
   - "WebSocket connection failed" → Backend not running
   - "Microphone denied" → Browser permission issue
   - "Audio playback blocked" → Browser autoplay policy

---

## ✅ Step-by-Step Fix

### Step 1: Update Backend

Make sure you have latest version:

```bash
cd backend
git pull origin main  # Get latest code
```

### Step 2: Restart Backend

```bash
# Terminal where backend is running:
# Press Ctrl+C to stop

uvicorn main:app --reload

# Should see:
# ✅ TTS initialized with provider: pyttsx3 (local, works offline)
```

### Step 3: Hard Refresh Browser

1. Go to http://localhost:3000
2. Press **Ctrl+Shift+R** (hard refresh, clears cache)
3. Wait for page to load

### Step 4: Check Microphone

1. Click "📞 Call Clinic"
2. **Browser asks for microphone**
3. Click **"Allow"** (not "Block")
4. You should hear AI greeting

### Step 5: Verify in Backend Logs

You should see:
```
2026-01-03 12:57:23,651 - main - INFO - 📞 New call connected
2026-01-03 12:57:23,651 - main - INFO - 🎤 Agent: Hello, thank you for calling Local Medical Clinic...
```

If you see this = **Everything working!** ✅

---

## 🐛 Troubleshooting

### Problem: Still No Sound

**Check 1: Is backend running?**
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy",...}
```

**Check 2: Is Ollama running?**
```bash
curl http://localhost:11434/api/tags
# Should return: {"models":[{"name":"llama2:latest"...}]}
```

**Check 3: Browser console errors**
1. Press F12
2. Go to Console tab
3. Look for red errors
4. Check Network tab (WebSocket connection)

### Problem: Audio is Choppy/Slow

**Cause**: pyttsx3 is slower than gTTS

**Solution**: Use gTTS (requires internet):

**Edit `backend/.env`:**
```env
TTS_PROVIDER=gtts
```

Restart backend:
```bash
uvicorn main:app --reload
```

**Requirement**: Must have internet connection

### Problem: pyttsx3 Not Working

**Symptom**: Error about pyttsx3 not installed

**Fix**:
```bash
cd backend
pip install pyttsx3
uvicorn main:app --reload
```

### Problem: Browser Won't Allow Microphone

1. **Reset microphone permission:**
   - Chrome/Edge: Settings → Privacy → Microphone → Allow
   - Firefox: Preferences → Privacy → Permissions → Microphone → Allow

2. **Refresh page**:
   - Press Ctrl+F5

3. **Try again:**
   - Click "📞 Call Clinic"
   - Click "Allow" when prompted

---

## 🔍 Debug: Check Everything Works

### Terminal 1: Verify All Services Running

```bash
# Check Ollama
curl http://localhost:11434/api/tags
# Should return models

# Check Backend
curl http://localhost:8000/health
# Should return: {"status":"healthy"}

# Check Frontend
curl http://localhost:3000
# Should return HTML
```

All three working = **System is ready** ✅

### Terminal 2: Monitor Backend Logs

Keep backend terminal visible. When you call:

```
2026-01-03 12:57:23,651 - main - INFO - 📞 New call connected
2026-01-03 12:57:23,651 - audio.tts - INFO - pyttsx3 synthesized X characters
2026-01-03 12:57:23,681 - main - INFO - 🎤 Agent: [response]
```

If you see all these lines = **Audio pipeline working** ✅

### Browser DevTools: Check Network

1. Press F12
2. Go to Network tab
3. Filter by "WS" (WebSocket)
4. Click "📞 Call Clinic"
5. You should see `/ws` connection
6. Status should be "101 Switching Protocols" (green)

If you see this = **Frontend connection working** ✅

---

## 🌟 Audio Flow Diagram

```
┌─────────────────────────┐
│   Browser (Frontend)    │
│  http://localhost:3000  │
│                         │
│ Click "📞 Call Clinic"  │
└────────┬────────────────┘
         │
         │ WebSocket /ws
         │ (real-time audio)
         │
         v
┌─────────────────────────┐
│  Backend (FastAPI)      │
│  http://localhost:8000  │
│                         │
│ 1. Get greeting text    │
│ 2. Convert to speech    │
│    (pyttsx3)            │
│ 3. Send audio back      │
└────────┬────────────────┘
         │
         │ WebSocket (audio bytes)
         │
         v
┌─────────────────────────┐
│  Browser Audio Playback │
│                         │
│ 🔊 You hear greeting!   │
└─────────────────────────┘

┌─────────────────────────┐
│  You Speak (Microphone) │
└────────┬────────────────┘
         │
         │ Audio bytes
         │
         v
┌─────────────────────────┐
│  Backend (FastAPI)      │
│                         │
│ 1. Receive audio        │
│ 2. Send to Ollama       │
│ 3. Get response         │
│ 4. Convert to speech    │
│ 5. Send back            │
└────────┬────────────────┘
         │
         │ WebSocket (audio bytes)
         │
         v
┌─────────────────────────┐
│  Browser Audio Playback │
│                         │
│ 🔊 You hear response!   │
└─────────────────────────┘
```

---

## ✅ Complete Checklist

```
[ ] Downloaded latest code (git pull)
[ ] Backend restarted (Ctrl+C then uvicorn...)
[ ] Browser hard refreshed (Ctrl+Shift+R)
[ ] Backend shows: "✅ TTS initialized with pyttsx3"
[ ] Frontend: http://localhost:3000 loads
[ ] Clicked "📞 Call Clinic" button
[ ] Microphone permission: "Allow"
[ ] Backend shows: "📞 New call connected"
[ ] Heard AI greeting
[ ] Spoke into microphone
[ ] Heard AI response
```

If all checked = **Everything works!** 🎉

---

## 🎉 Expected Behavior

### When You Call

1. Click "📞 Call Clinic"
2. Backend terminal shows: `📞 New call connected`
3. **Hear AI voice**: "Hello, thank you for calling..."
4. Say something: "I want an appointment"
5. **Hear AI response**: "What service would you like?"
6. Continue conversation naturally

### If Something Missing

- No greeting audio?
  → TTS issue (use gtts or check pyttsx3)
- No response to your voice?
  → Check backend logs for errors
- Connection keeps dropping?
  → Check WebSocket connection in DevTools

---

## 📀 Files Modified

| File | Change |
|------|--------|
| `backend/audio/tts.py` | Default to pyttsx3, with fallback |
| `backend/.env` | Changed TTS_PROVIDER to pyttsx3 |

---

## 🚀 Next Steps

1. **Update code**: `git pull origin main`
2. **Restart backend**: `uvicorn main:app --reload`
3. **Hard refresh browser**: Ctrl+Shift+R
4. **Try calling**: Click "📞 Call Clinic"
5. **Check logs**: See if greeting audio plays

---

**Your audio should now work!** 🔊

If still having issues, check:
- Backend logs (should show TTS initialized)
- Browser console (F12)
- Network tab (WebSocket connection)

