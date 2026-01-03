# 🔍 Debug: Voice Not Being Processed

**Problem**: Greeting plays, but when you speak, nothing happens. Backend doesn't receive or process your voice.

---

## 📊 What's Happening (or Not)

**Expected Flow:**
```
✅ You speak
✅ Frontend captures audio
✅ Frontend sends via WebSocket
✅ Backend receives bytes
✅ Backend logs: 📊 Received audio chunk: X bytes
✅ Backend detects speech (VAD)
✅ Backend transcribes (STT)
✅ Backend logs: 👤 User: [your text]
✅ Backend sends to AI
✅ Backend logs: 🎤 Agent: [response]
✅ Backend sends audio
✅ You hear response
```

**What's Actually Happening:**
```
✅ You speak
✅ Frontend captures audio
✅ Frontend sends via WebSocket
❌ Backend DOESN'T LOG: 📊 Received audio chunk
❌ Nothing else happens
```

**Root Cause**: Backend is **NOT RECEIVING audio bytes** from frontend.

---

## 🔊 Enable Debug Logging

**I've already updated `.env` to enable DEBUG logging.**

Restart backend to see detailed logs:

```bash
cd backend
# Press Ctrl+C to stop

# Restart with debug logging
uvicorn main:app --reload
```

**You should now see TONS of debug messages:**

```
2026-01-03 23:58:22,008 - main - INFO - 🏥 AI Call Agent starting...
2026-01-03 23:58:22,048 - main - INFO - ✅ Clinic agent initialized
2026-01-03 23:58:22,048 - main - INFO - ✅ System ready to receive calls
INFO:     Application startup complete.
INFO:     ('127.0.0.1', 63995) - "WebSocket /ws" [accepted]
2026-01-03 23:59:04,071 - main - INFO - 📞 New call connected
2026-01-03 23:59:04,072 - main - INFO - 🎤 Agent: Hello, thank you for calling...
INFO:     connection open
🐛 DEBUG LOGS APPEAR HERE WHEN YOU SPEAK
```

---

## 🏆 Test Step-by-Step

### Step 1: Restart Backend with Debug Logs

```bash
cd backend

# Get latest code
git pull origin main

# Stop current server (Ctrl+C)

# Restart
uvicorn main:app --reload

# Watch for: LOG_LEVEL=DEBUG messages
```

### Step 2: Check Frontend Connection

```bash
# Hard refresh browser
http://localhost:3000
Ctrl+Shift+R
```

### Step 3: Open Browser DevTools

1. **Press F12**
2. **Go to Console tab**
3. **Look for any RED ERRORS**
4. **Go to Network tab**
5. **Filter by "WS" (WebSocket)**

### Step 4: Make a Call

1. Click **♠️ Call Clinic**
2. Allow microphone
3. Hear greeting
4. **Speak a few words**
5. **Pause for 2 seconds** (silence triggers sending)

### Step 5: Watch Backend Logs

**You should see in backend terminal:**

```
📞 New call connected
🎤 Agent: Hello, thank you for calling...
📤 Sending greeting audio: 5234 bytes
🎧 Waiting for user audio...

[You speak here for 2-3 seconds]
📥 Receiving from WebSocket...   ← SHOULD APPEAR
📊 Received audio chunk: 4096 bytes  ← SHOULD APPEAR
🔍 Running Voice Activity Detection...  ← SHOULD APPEAR
🔍 VAD result: True  ← IF THIS IS FALSE, YOUR MIC IS TOO QUIET
🎤 Starting Speech-to-Text...
📝 Transcription result: 'I have problems with my heart'  ← SHOULD APPEAR
👤 User: I have problems with my heart
🧠 Sending to agent...
🎤 Agent: I understand you're experiencing heart issues...
🔊 Converting response to speech...
📤 Sending response audio: 8934 bytes
✅ Message #1 completed
```

---

## 🐛 What to Look For

### ✅ **SUCCESS: You Should See**

```
📥 Receiving from WebSocket...   ✅ CRITICAL
📊 Received audio chunk: 4096 bytes  ✅ CRITICAL
🔍 VAD result: True              ✅ CRITICAL
📝 Transcription result: '...'   ✅ CRITICAL
```

If you see these 4 = **Audio is flowing correctly!**

### ❌ **FAILURE: If You DON'T See**

```
❌ 📥 Receiving from WebSocket...   ← FRONTEND NOT SENDING
```

This means **frontend is not sending audio to backend**.

### ❌ **FAILURE: If VAD Says False**

```
🔍 VAD result: False  ← VOICE TOO QUIET
```

Your microphone audio is too quiet. Try:
- Speaking LOUDER
- Moving mic closer
- Checking mic volume in Windows

### ❌ **FAILURE: If STT Returns Empty**

```
📝 Transcription result: ''  ← GOOGLE STT FAILED
```

Google Speech Recognition couldn't understand. Try:
- Speaking more clearly
- Checking internet connection
- Reducing background noise

---

## 🔏 Debugging Checklist

### Frontend Issues

```
[ ] Browser console (F12) - any RED errors?
[ ] Network tab - WebSocket connected? (status 101)
[ ] Microphone - permission granted?
[ ] Microphone - actually working?
[ ] Audio not too quiet?
```

**Test microphone:**
1. Open http://localhost:3000
2. Open DevTools (F12)
3. Go to Console
4. Paste:
```javascript
navigator.mediaDevices.getUserMedia({audio:true})
  .then(stream => console.log("Mic works!", stream))
  .catch(err => console.error("Mic failed", err))
```
5. If you see "Mic works" = microphone is accessible

### Backend Issues

```
[ ] Backend logs show "Clinic agent initialized"?
[ ] Backend logs show debug messages when you speak?
[ ] VAD showing True or False?
[ ] STT showing transcription result?
[ ] Backend processing audio OR waiting?
```

**Check specific components:**

```bash
# Test if backend is running
curl http://localhost:8000/health

# Test if Ollama is running
curl http://localhost:11434/api/tags

# Test if TTS works
curl -X POST "http://localhost:8000/debug/tts?text=hello"
```

---

## 🐛 Most Likely Issues

### Issue 1: Frontend Not Sending Audio (Most Common)

**Symptom**: No log messages appear when you speak

**Check**:
1. Browser DevTools → Network tab → WebSocket connected?
2. Browser Console → Any RED errors?
3. Microphone permission granted?

**Fix**:
```bash
# Hard refresh browser
http://localhost:3000
Ctrl+Shift+R

# Check browser console for errors
F12 → Console tab
```

### Issue 2: Microphone Too Quiet

**Symptom**: Logs show `🔍 VAD result: False`

**Fix**:
- Speak **LOUDER**
- Move mic **CLOSER**
- Check Windows volume mixer

### Issue 3: Google STT Failing

**Symptom**: Logs show `📝 Transcription result: ''`

**Fix**:
- Check internet connection
- Speak **MORE CLEARLY**
- Reduce background noise
- Use OpenAI Whisper:
  ```bash
  # Add to backend/.env
  OPENAI_API_KEY=sk-your-key-here
  ```

### Issue 4: Ollama Not Responding

**Symptom**: `🧠 Sending to agent...` but no response

**Check**:
```bash
curl http://localhost:11434/api/tags

# Should return models, if not:
ollama list  # Check models
ollama serve  # Restart (if not auto-running)
```

---

## 👋 Browser DevTools Debugging

### Check WebSocket Connection

1. **Open DevTools**: F12
2. **Network tab**
3. **Filter**: Type "ws"
4. **Click ♠️ Call Clinic**
5. **Look for**: `/ws` connection

**Status should be**:
- `101 Switching Protocols` = Connected ✅
- `Failed` or `Pending` = Problem ❌

### Check JavaScript Errors

1. **Open DevTools**: F12
2. **Console tab**
3. **Look for**: RED text

**Common errors**:
- "Cannot access microphone" = Permission denied
- "WebSocket closed" = Backend not running
- "Unauthorized" = CORS issue

---

## 📤 Audio Flow

```
┌────────────────────────────────┐
│ 1. You Speak (Microphone)         │
└────────┬──────────────────────┘
         │
         │ WebAudio API analyzes
         │ 🐛 ISSUE: May not be capturing
         │
         v
┌────────────────────────────────┐
│ 2. Frontend records audio         │
│    MediaRecorder API               │
└────────┬──────────────────────┘
         │
         │ Send via WebSocket
         │ 🐛 ISSUE: May not be sending
         │ Check: Network tab shows data?
         │
         v
┌────────────────────────────────┐
│ 3. Backend receives bytes          │
│    📥 Receiving from WebSocket  │
│ 🐛 ISSUE: If not logged, above failed │
└────────┬──────────────────────┘
         │
         │ VAD: Detect speech
         │ 🐛 ISSUE: VAD=False? Mic too quiet
         │
         v
┌────────────────────────────────┐
│ 4. STT: Transcribe to text         │
│    Google Speech Recognition      │
│ 🐛 ISSUE: Empty result? Bad audio │
└────────┬──────────────────────┘
         │
         │ Send to Ollama AI
         │ Get response
         │
         v
┌────────────────────────────────┐
│ 5. TTS: Convert to speech           │
│    pyttsx3 or gTTS                 │
└────────┬──────────────────────┘
         │
         │ Send audio via WebSocket
         │
         v
┌────────────────────────────────┐
│ 6. Browser plays audio             │
│    You hear response 🔊           │
└────────────────────────────────┘
```

**Problem likely at Step 2 or 3** (frontend capturing/sending)

---

## ✅ Action Plan

1. **Pull latest code**: `git pull origin main`
2. **Restart backend**: `uvicorn main:app --reload`
3. **Hard refresh browser**: Ctrl+Shift+R
4. **Open DevTools**: F12 → Network & Console tabs
5. **Call clinic**: Click button
6. **Speak**: Say a few words
7. **Watch logs**: Look for "Received audio chunk" message
8. **Report**: What do you see in backend logs?

---

**Share backend logs from when you speak and I can diagnose exactly!** 🗐
