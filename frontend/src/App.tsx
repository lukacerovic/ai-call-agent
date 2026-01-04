import React, { useEffect, useState } from 'react';
import { useVoiceAgent } from './hooks/useVoiceAgent';
import './App.css';

/**
 * AI Voice Agent - Medical Clinic Call System
 * 
 * Architecture:
 * Frontend (React):
 *   - Audio capture with microphone
 *   - Voice Activity Detection (VAD)
 *   - Speech-to-Text (Web Speech API)
 *   - Text-to-Speech (Web Speech API)
 * 
 * Backend (FastAPI):
 *   - Session management
 *   - Chat API (text in, text out)
 *   - AI Agent (Ollama/OpenAI)
 */

function App() {
  const agent = useVoiceAgent();
  const [isInitialized, setIsInitialized] = useState(false);
  const [isCallActive, setIsCallActive] = useState(false);
  const [log, setLog] = useState<string[]>([]);

  // Initialize on mount
  useEffect(() => {
    const init = async () => {
      try {
        const success = await agent.initialize();
        setIsInitialized(success);
      } catch (err) {
        console.error('Initialization failed:', err);
      }
    };

    init();
  }, []);

  // Override console.log to show in UI
  useEffect(() => {
    const originalLog = console.log;
    const originalError = console.error;
    const originalWarn = console.warn;

    console.log = (...args: any[]) => {
      const message = args.join(' ');
      setLog((prev) => [...prev.slice(-50), message]); // Keep last 50 messages
      originalLog(...args);
    };

    console.error = (...args: any[]) => {
      const message = '❌ ' + args.join(' ');
      setLog((prev) => [...prev.slice(-50), message]);
      originalError(...args);
    };

    console.warn = (...args: any[]) => {
      const message = '⚠️  ' + args.join(' ');
      setLog((prev) => [...prev.slice(-50), message]);
      originalWarn(...args);
    };

    return () => {
      console.log = originalLog;
      console.error = originalError;
      console.warn = originalWarn;
    };
  }, []);

  const handleStartCall = async () => {
    try {
      setIsCallActive(true);
      await agent.startConversation();
    } catch (err) {
      console.error('Call failed:', err);
      setIsCallActive(false);
    }
  };

  const handleEndCall = async () => {
    try {
      window.speechSynthesis.cancel();
      await agent.stopRecording();
      setIsCallActive(false);
    } catch (err) {
      console.error('Failed to end call:', err);
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <h1>🏥 AI Medical Clinic</h1>
          <p>Voice-Powered AI Receptionist</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="app-main">
        {/* Status Panel */}
        <div className="panel status-panel">
          <div className="panel-header">
            <h2>📊 System Status</h2>
          </div>
          <div className="panel-body">
            <div className="status-item">
              <span className="status-label">Initialization:</span>
              <span className={`status-value ${isInitialized ? 'success' : 'pending'}`}>
                {isInitialized ? '✅ Ready' : '⏳ Loading...'}
              </span>
            </div>
            <div className="status-item">
              <span className="status-label">Call Status:</span>
              <span className={`status-value ${isCallActive ? 'active' : 'idle'}`}>
                {isCallActive ? '🔴 Active' : '⚪ Idle'}
              </span>
            </div>
            <div className="status-item">
              <span className="status-label">Session ID:</span>
              <code className="session-id">
                {agent.sessionId
                  ? agent.sessionId.substring(0, 12) + '...'
                  : 'Not created'}
              </code>
            </div>
            <div className="status-item">
              <span className="status-label">State:</span>
              <span className={`status-badge ${agent.state}`}>{agent.state}</span>
            </div>
          </div>
        </div>

        {/* Control Panel */}
        <div className="panel control-panel">
          <div className="panel-header">
            <h2>📞 Call Controls</h2>
          </div>
          <div className="panel-body">
            {!isCallActive ? (
              <button
                className="btn btn-primary btn-lg"
                onClick={handleStartCall}
                disabled={!isInitialized}
              >
                ☎️ Call Clinic
              </button>
            ) : (
              <button className="btn btn-danger btn-lg" onClick={handleEndCall}>
                🛑 End Call
              </button>
            )}
          </div>
        </div>

        {/* Console Log */}
        <div className="panel console-panel">
          <div className="panel-header">
            <h2>📺 Console Output</h2>
            <button
              className="btn btn-sm"
              onClick={() => setLog([])}
              title="Clear logs"
            >
              🗑️ Clear
            </button>
          </div>
          <div className="console">
            {log.length === 0 ? (
              <div className="console-empty">Waiting for logs...</div>
            ) : (
              log.map((message, index) => (
                <div key={index} className="console-line">
                  {message}
                </div>
              ))
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>
          Frontend: Voice Capture + Web Speech API | Backend: OpenAI Agent + Ollama
        </p>
      </footer>
    </div>
  );
}

export default App;
