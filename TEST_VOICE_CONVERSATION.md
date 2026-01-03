# 📞 Test: Full Voice Conversation Flow

**New feature: Frontend now properly captures and sends voice!**

This guide explains the exact conversation flow you should see.

---

## 🚀 Quick Start (3 Minutes)

### **Step 1: Pull Latest Code**

```bash
cd ai-call-agent
git pull origin main
```

### **Step 2: Restart Backend**

```bash
cd backend
# Press Ctrl+C to stop

uvicorn main:app --reload
```

### **Step 3: Restart Frontend**

```bash
cd frontend
# Press Ctrl+C to stop

npm start
```

### **Step 4: Open Browser DevTools**

```
http://localhost:3000
Press F12
Go to: Console tab
```

You'll see LOTS of debug messages showing the voice flow.

---

## 🏆 Expected Conversation Flow

### **1. You Click ☎️ Call Clinic**

**Frontend Console Shows:**
```
✅ Microphone access granted
📡 Connecting to WebSocket: ws://localhost:8000/ws
✅ WebSocket connected
🎤 Starting voice capture...
```

**Backend Shows:**
```
📞 New call connected
🎤 Agent: Hello, thank you for calling Local Medical Clinic...
📤 Sending greeting audio: 5234 bytes
🎧 Waiting for user audio...
```

**You Hear:** AI greeting about clinic services

**Status:** "Listening..."

---

### **2. You Start Speaking**

Example: *"I am having problems with my heart and I need to check it fast. Can you suggest which service should I take?"*

**Frontend Console Shows:**
```
🔴 Speech detected, starting recording
```

**Status:** Changes to "Listening..."

**What's Happening:** 
- Microphone captures your voice
- MediaRecorder records audio chunks
- Frontend analyzes frequency to detect speech

---

### **3. You Stop Speaking (Silence for 2-3 seconds)**

**Frontend Console Shows:**
```
🔇 Silence detected (1/15)
🔇 Silence detected (2/15)
🔇 Silence detected (3/15)
...
🔇 Silence detected (15/15)
⏹️ Silence duration reached, stopping recording and sending
📝 Audio chunk received: 4096 bytes
📦 Compiled audio blob: 48234 bytes
📤 Sending audio to backend: 48234 bytes
```

**What's Happening:**
- Frontend detects 1.5 seconds of silence
- Stops recording your voice
- Converts WebM audio to blob
- Sends via WebSocket to backend
- Shows: "[Processing your speech...]"

---

### **4. Backend Receives and Processes**

**Backend Shows:**
```
📥 Receiving from WebSocket...
📊 Received audio chunk: 48234 bytes
🔍 Running Voice Activity Detection...
🔍 VAD result: True (speech detected)
🎤 Starting Speech-to-Text...
📝 Transcription result: 'I am having problems with my heart...'
👤 User: I am having problems with my heart and I need to check it fast. Can you suggest which service should I take?
```

**What's Happening:**
- Backend receives audio bytes
- Voice Activity Detection confirms speech
- Google Speech Recognition transcribes to text
- Text sent to Ollama AI agent

---

### **5. AI Agent Processes and Responds**

**Backend Shows:**
```
🧠 Sending to agent: 'I am having problems with my heart...'
🎤 Agent: I understand you're experiencing heart-related concerns. For heart issues, I recommend our Cardiology service. Let me help you schedule an appointment with one of our cardiologists. What date and time would work best for you?
🔊 Converting response to speech...
📤 Sending response audio: 8934 bytes
✅ Message #1 completed
```

**What's Happening:**
- Ollama LLM processes your message
- Generates natural response
- pyttsx3 converts to speech (offline)
- Sends audio back to frontend

---

### **6. You Hear AI Response**

**Frontend Console Shows:**
```
📥 Received from backend: 8934 bytes
🔊 Playing audio: 8934 bytes
▶️ Audio started playing
```

**You Hear:** *"I understand you're experiencing heart-related concerns..."*

**Status:** Changes to "Agent Speaking..."

---

### **7. AI Finishes Speaking, Loop Repeats**

**Frontend Console Shows:**
```
⏹️ Audio finished playing
🎤 Starting voice capture...
```

**Status:** Changes back to "Listening..."

**What's Happening:**
- After AI finishes speaking
- Frontend automatically starts listening again
- Ready for your next message

---

### **8. You Respond to Agent**

Example: *"I prefer next Tuesday at 2 PM"*

**The loop repeats:** Speech detection → Silence → Send → Process → Response → Listen

---

### **9. You End Call**

Click **📵 End Call**

**Frontend Console Shows:**
```
📵 Ending call
🛑 Stopping audio capture
🔌 WebSocket disconnected
```

**Backend Shows:**
```
📞 Call disconnected
📊 Call session session-1234567890.123456 ended (messages processed: 3)
```

---

## 🐛 Console Debug Messages

### Frontend (Browser Console - F12)

**Good signs:**
```
✅ Microphone access granted
✅ WebSocket connected
🔴 Speech detected, starting recording
⏹️ Silence duration reached, stopping recording and sending
📤 Sending audio to backend: X bytes
🔊 Playing audio: X bytes
```

**Bad signs:**
```
❌ Microphone access denied
❌ WebSocket error
❌ Failed to play audio
```

### Backend (Terminal Output)

**Good signs:**
```
📥 Receiving from WebSocket...
📊 Received audio chunk: X bytes
🔍 VAD result: True
📝 Transcription result: 'user text'
👤 User: user text
🎤 Agent: response text
📤 Sending response audio: X bytes
```

**Bad signs:**
```
❌ No "Received audio chunk" messages
🔍 VAD result: False (microphone too quiet)
📝 Transcription result: '' (empty - bad audio quality)
```

---

## 🔊 How Voice Detection Works

### **Speech Detection (Frontend)**

```
Microphone Audio Stream
        ↓
   Analyze Frequency
        ↓
   Is Average > 25? (Threshold)
        ↓
    YES: Recording ON 🔴
    NO:  Silence Counter++
        ↓
   Silence Counter >= 15? (1.5 seconds)
        ↓
    YES: Stop Recording & Send 📤
    NO:  Continue Listening
```

### **Why 2-3 Seconds Silence?**

- **Natural speech pattern:** People naturally pause between thoughts
- **Prevents accidental sending:** Short pauses within sentences don't trigger send
- **Detects end of message:** 1.5 second pause = confident message is complete

**Example:**
- "I have... [0.3s pause]... heart problems" → Still recording (pause < 1.5s)
- "I have heart problems" → [2 second silence] → Send! (silence >= 1.5s)

---

## 🔡 How STT (Speech-to-Text) Works

### **Flow:**

```
Audio Blob (WebM format)
        ↓
   Backend Receives
        ↓
   Voice Activity Detection (VAD)
   - Is this actual speech? YES ✅
        ↓
   Google Speech Recognition
   - Convert audio to text
   - "I have heart problems"
        ↓
   Ollama AI Agent
   - Process message
   - Generate response
        ↓
   pyttsx3 Text-to-Speech
   - Convert response to audio
        ↓
   Send Audio Back to Frontend
```

---

## ✅ Checklist: Voice Conversation Working?

```
[ ] Click ☎️ Call Clinic
[ ] Hear AI greeting
[ ] Status shows "Listening..."
[ ] Speak into microphone
[ ] Frontend console shows: "🔴 Speech detected, starting recording"
[ ] Pause for 2-3 seconds
[ ] Frontend console shows: "⏹️ Silence duration reached, stopping recording and sending"
[ ] Backend console shows: "📊 Received audio chunk"
[ ] Backend console shows: "📝 Transcription result: '[your speech]'"
[ ] Backend console shows: "👤 User: [your speech]"
[ ] Backend console shows: "🎤 Agent: [response]"
[ ] Backend console shows: "📤 Sending response audio"
[ ] You hear AI response
[ ] Status changes back to "Listening..."
[ ] Speak again - conversation continues
[ ] Click 📵 End Call to disconnect
```

**All checked? Voice system is working!** 🎉

---

## 🐛 Troubleshooting

### Problem: Frontend doesn't show "Speech detected" message

**Cause:** Microphone not capturing audio or threshold too high

**Fix:**
- Speak LOUDER
- Get mic CLOSER to mouth
- Reduce background noise
- Check Windows Volume Mixer

### Problem: Backend shows "VAD result: False"

**Cause:** Audio too quiet for voice detection

**Fix:** Same as above - speak louder

### Problem: Backend shows empty transcription

**Cause:** Google Speech Recognition couldn't understand

**Fix:**
- Speak more clearly
- Reduce background noise
- Check internet connection (Google STT needs it)

### Problem: No audio response from AI

**Cause:** Either:
1. Ollama not responding
2. TTS conversion failed
3. WebSocket not open

**Fix:**
- Check Ollama: `curl http://localhost:11434/api/tags`
- Check backend logs for errors
- Restart backend

---

## 🎯 Architecture

```
┌────────────────────────────────┐
│          FRONTEND (React)             │
│       http://localhost:3000          │
│                                      │
│   1. Capture Microphone Audio       │
│   2. Detect Speech vs Silence       │
│   3. Convert to Audio Blob          │
│   4. Send via WebSocket             │
│   5. Play Response Audio            │
└────────┬──────────────────────┘
         │
         │ WebSocket /ws (Real-time Audio)
         │ Bi-directional, encrypted
         │
         v
┌────────────────────────────────┐
│         BACKEND (FastAPI)           │
│       http://localhost:8000         │
│                                      │
│   1. Receive Audio Bytes            │
│   2. Voice Activity Detection       │
│   3. Speech-to-Text (Google)       │
│   4. Send to Ollama AI              │
│   5. Text-to-Speech (pyttsx3)      │
│   6. Send Response Audio            │
└────────┬──────────────────────┘
         │
         │ HTTP (Ollama Integration)
         │
         v
┌────────────────────────────────┐
│          OLLAMA (Local AI)          │
│       http://localhost:11434        │
│                                      │
│   LLM: llama2                        │
│   - Understands patient needs      │
│   - Generates intelligent responses │
│   - Offline (private)               │
└────────────────────────────────┘
```

---

## 🚀 Ready to Test?

1. **Get latest code**: `git pull origin main`
2. **Restart backend**: `uvicorn main:app --reload`
3. **Restart frontend**: `npm start`
4. **Open DevTools**: F12 → Console
5. **Call clinic**: Click button
6. **Speak naturally**: Say something about your health
7. **Pause for 2-3 seconds**: Signals end of message
8. **Listen for response**: AI replies naturally
9. **Continue conversation**: Loop repeats

**Your voice conversation system is now complete!** 🎉
