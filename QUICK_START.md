# ⚡ Quick Start - 5 Minutes

## On Windows

```batch
REM 1. Run setup script
setup-windows.bat

REM 2. Edit your API keys
REM Edit: backend\.env
REM Add: OPENAI_API_KEY=sk-...
REM Add: GROQ_API_KEY=gsk-...

REM 3. Terminal 1 - Backend
cd backend
venv\Scripts\activate
uvicorn main:app --reload

REM 4. Terminal 2 - Frontend (while backend runs)
cd frontend
npm start

REM 5. Browser opens automatically
REM Click "Call Clinic" button
```

## On macOS/Linux

```bash
# 1. Clone
git clone https://github.com/lukacerovic/ai-call-agent.git
cd ai-call-agent

# 2. Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your keys

# 3. Terminal 1 - Start Backend
uvicorn main:app --reload

# 4. Terminal 2 - Start Frontend
cd frontend
npm install
npm start

# 5. Browser opens at http://localhost:3000
```

## Get API Keys

### OpenAI (REQUIRED)
- Go: https://platform.openai.com/api-keys
- Create key
- Copy to `backend/.env` as `OPENAI_API_KEY=sk-...`

### Groq (RECOMMENDED for LLM)
- Go: https://groq.com/
- Sign up
- Get API key
- Copy to `backend/.env` as `GROQ_API_KEY=gsk-...`

## Check It Works

```bash
# Backend health
curl http://localhost:8000/health

# Frontend
open http://localhost:3000  # macOS
start http://localhost:3000 # Windows
```

## Make Your First Call

1. ✅ Backend running on http://localhost:8000
2. ✅ Frontend running on http://localhost:3000
3. ✅ Click "📞 Call Clinic" button
4. ✅ Allow microphone
5. ✅ Listen to AI greeting
6. ✅ Speak your message
7. ✅ AI responds
8. ✅ Conversation continues
9. ❌ Say "Goodbye" to end

## Troubleshoot

| Problem | Solution |
|---------|----------|
| Python not found | Install Python 3.10 or 3.11 from python.org |
| Module not found | Activate venv: `venv\Scripts\activate` |
| Port 8000 in use | Kill process or use: `uvicorn main:app --port 8001` |
| No microphone | Browser permissions: Allow microphone |
| No API key error | Edit `backend/.env` with your keys |
| WebSocket error | Backend must be running on 8000 |

## More Help

- 📖 Full guide: `SETUP.md`
- 🐛 Issues: GitHub Issues
- 🎯 Backend docs: http://localhost:8000/docs

---

**That's it! You're ready to go! 🚀**
