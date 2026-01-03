# 🏥 AI Call Agent – Medical Clinic Voice Support System

An AI-powered phone-call-style customer support system for medical clinics. The system simulates a real phone conversation with automatic speech recognition, voice activity detection, and intelligent voice responses.

## ✨ Features

- 📞 **Phone Call Simulation** – Press one button to call the clinic
- 🎙️ **Voice-Only Interaction** – No text input, forms, or buttons during the call
- 🧠 **Intelligent AI Agent** – Powered by LLaMA 3.2 with OpenAI structure
- 🔄 **Full Duplex Conversation** – Listen → Transcribe → Reason → Speak → Listen loop
- 🎧 **Advanced Audio Pipeline** – VAD, STT, TTS with silence detection
- 💾 **Context-Aware** – Remembers conversation history and confirms details
- 🏥 **Medical-Appropriate** – Professional, calm, and safe responses with disclaimers

## 🏗️ Tech Stack

### Backend
- **FastAPI** – High-performance Python web framework
- **OpenAI Agent** – Structured conversational AI
- **LLaMA 3.2** – Large Language Model
- **WebSocket** – Real-time streaming communication
- **pyannote** – Voice Activity Detection (VAD)
- **Whisper** – Speech-to-Text (OpenAI)
- **pyttsx3/gTTS** – Text-to-Speech

### Frontend
- **React** – JavaScript UI library
- **Web Audio API** – Microphone & audio recording
- **TypeScript** – Type-safe development

## 📋 Project Structure

```
ai-call-agent/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── agents/
│   │   ├── clinic_agent.py     # AI Agent logic
│   │   ├── llm_config.py       # LLaMA 3.2 configuration
│   │   └── memory.py           # Conversation context manager
│   ├── audio/
│   │   ├── vad.py             # Voice Activity Detection
│   │   ├── stt.py             # Speech-to-Text (Whisper)
│   │   └── tts.py             # Text-to-Speech
│   ├── data/
│   │   ├── services.json       # Available medical services
│   │   └── reservations.json   # Booking database
│   ├── requirements.txt        # Python dependencies
│   └── .env.example            # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CallInterface.tsx    # Main call UI
│   │   │   ├── CallButton.tsx       # Single call button
│   │   │   └── AudioVisualizer.tsx  # Real-time audio indicator
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts      # WebSocket connection
│   │   │   └── useMicrophone.ts     # Microphone control
│   │   ├── App.tsx             # Main app component
│   │   ├── index.tsx           # React entry point
│   │   └── styles/
│   │       └── App.css         # Global styles
│   ├── package.json            # Node dependencies
│   ├── tsconfig.json           # TypeScript config
│   └── public/
│       └── index.html          # HTML template
├── docker-compose.yml          # Multi-service orchestration
├── Dockerfile                  # Backend container
├── .gitignore
└── README.md                   # This file

```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (optional)
- OpenAI API Key
- Ollama (for LLaMA 3.2) or Groq API

### Environment Setup

1. **Clone the repository**
```bash
git clone https://github.com/lukacerovic/ai-call-agent.git
cd ai-call-agent
```

2. **Create `.env` file**
```bash
cp backend/.env.example backend/.env
```

3. **Configure `.env`**
```env
# OpenAI API
OPENAI_API_KEY=your_key_here

# LLaMA Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Or use Groq instead
GROQ_API_KEY=your_groq_key_here
GROQ_MODEL=llama-3.2-70b-versatile

# Frontend
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws
```

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will open at `http://localhost:3000`.

### Docker Setup (Optional)

```bash
docker-compose up --build
```

This starts:
- Backend API (http://localhost:8000)
- Frontend (http://localhost:3000)
- Ollama (optional, for local LLM)

## 📚 API Endpoints

### WebSocket
- `WS /ws` – Real-time audio streaming and responses

### REST Endpoints
- `GET /health` – Health check
- `GET /services` – List available services
- `POST /reservations` – Create appointment
- `GET /reservations/{patient_id}` – Get patient's appointments

## 🎤 Voice Interaction Flow

```
User presses "Call Clinic"
    ↓
Microphone activates
    ↓
AI speaks greeting: "Hello, thank you for calling..."
    ↓
[LOOP]
    Listen for user input
    Detect silence (1-1.5 seconds)
    Transcribe speech → text
    AI processes context
    Generate response
    Convert to speech
    Play audio
    Listen again
[END LOOP]
    ↓
User says "goodbye" or timeout
    ↓
Connection closes
```

## 🧠 AI Agent Behavior

The agent is configured as a professional medical receptionist:

✅ **Behaviors:**
- Greets users warmly and professionally
- Asks one question at a time
- Listens completely before responding
- Asks clarifying questions when needed
- Confirms details verbally (name, DOB, appointment time)
- Provides information about services
- Books appointments
- Reads back details slowly and clearly

❌ **Never:**
- Diagnoses medical conditions
- Provides medical advice
- Makes assumptions about symptoms
- Escalates to emergency without user consent

## 📄 Data Files

### services.json
```json
[
  {
    "id": "consultation-001",
    "name": "Initial Consultation",
    "durationMinutes": 30,
    "price": 50,
    "description": "Meet with our healthcare provider",
    "whatIsIncluded": "Medical history review, vital signs check",
    "howItsDone": "In-person at clinic",
    "specialPreparation": null
  }
]
```

### reservations.json
```json
[
  {
    "id": "res-001",
    "serviceId": "consultation-001",
    "date": "2026-01-15",
    "time": "14:00",
    "patientName": "John Doe",
    "patientDOB": "1990-05-20"
  }
]
```

## 🔐 Safety & Medical Disclaimers

The system implements:
- ✅ Automatic disclaimer on call start
- ✅ Emergency escalation protocol
- ✅ No diagnosis capabilities
- ✅ Context-aware medical warnings
- ✅ Conversation logging for compliance

Example disclaimer:
> "Hello, thank you for calling our clinic. I'm an AI assistant. I can help you schedule appointments and provide general information, but I cannot provide medical diagnosis or emergency care. For emergencies, please call 911 or visit your nearest emergency room."

## 🛠️ Configuration

### Audio Settings
```python
# backend/audio/vad.py
VAD_THRESHOLD = 0.5
SILENCE_DURATION = 1.5  # seconds
CHUNK_SIZE = 1024
SAMPLE_RATE = 16000
```

### LLM Settings
```python
# backend/agents/llm_config.py
TEMPERATURE = 0.7  # Professional but natural
MAX_TOKENS = 150   # Keep responses concise
MODEL = "llama-3.2-70b-versatile"  # Via Groq or Ollama
```

## 📖 Development Guide

### Adding Custom Services
Edit `backend/data/services.json`:
```json
{
  "id": "dermatology-001",
  "name": "Dermatology Consultation",
  "durationMinutes": 45,
  "price": 75,
  "description": "Specialized skin care consultation",
  "whatIsIncluded": "Full skin examination, personalized treatment plan",
  "howItsDone": "In-person or telemedicine",
  "specialPreparation": "Come with clean skin, no makeup"
}
```

### Customizing AI Behavior
Edit `backend/agents/clinic_agent.py` to modify:
- Greeting message
- Available actions
- Response tone
- Confirmation protocols

### Integrating with Real Backend
Replace `reservations.json` with:
- PostgreSQL database
- REST API calls
- SMS/Email notifications

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Microphone not accessible | Check browser permissions and HTTPS (required by Web Audio API) |
| No audio from AI | Verify OpenAI/Groq API key and TTS configuration |
| VAD not detecting speech | Adjust `VAD_THRESHOLD` and `SILENCE_DURATION` |
| WebSocket connection fails | Check backend is running on correct port |
| LLaMA model not found | Install Ollama or configure Groq API |

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License – feel free to use this project commercially.

## 🔗 References

- [AI Court Project](https://github.com/lukacerovic/AI_Court) – Inspiration for agent architecture
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API](https://platform.openai.com/)
- [Groq API](https://groq.com/)
- [Whisper Documentation](https://github.com/openai/whisper)
- [pyannote.audio](https://github.com/pyannote/pyannote-audio)

## 📧 Support

For questions or issues, please open a GitHub issue or contact the development team.

---

**Made with ❤️ for medical clinics everywhere**
