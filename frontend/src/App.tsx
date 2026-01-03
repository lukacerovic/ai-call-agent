import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import useVoiceAgent from './hooks/useVoiceAgent';

function App() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [status, setStatus] = useState<'idle' | 'listening' | 'thinking' | 'speaking' | 'error'>('idle');
  const [isInCall, setIsInCall] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [sessionError, setSessionError] = useState<string | null>(null);
  const isSpeakingRef = useRef(false);

  // Initialize session
  useEffect(() => {
    const initializeSession = async () => {
      try {
        console.log('🔄 [SESSION] Initializing session...');
        const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
        console.log(`📡 [SESSION] API URL: ${apiUrl}/session/new`);
        
        const response = await fetch(`${apiUrl}/session/new`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        
        console.log(`📥 [SESSION] Response status: ${response.status}`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ [SESSION] Session created:', data);
        
        if (data.session_id) {
          setSessionId(data.session_id);
          setSessionError(null);
          console.log('✅ [SESSION] Session ID set:', data.session_id);
        } else {
          throw new Error('No session_id in response');
        }
      } catch (error) {
        console.error('❌ [SESSION] Failed to initialize session:', error);
        setSessionError(error instanceof Error ? error.message : 'Unknown error');
        const fallbackId = `fallback-${Date.now()}`;
        console.log('⚠️ [SESSION] Using fallback session ID:', fallbackId);
        setSessionId(fallbackId);
      }
    };

    initializeSession();
  }, []);

  // Handle AI responses
  const handleResponseReceived = (responseText: string) => {
    console.log('\n' + '='.repeat(80));
    console.log('📥 [RESPONSE] AI Response received');
    console.log('='.repeat(80));
    console.log(`📝 [RESPONSE] Text: ${responseText}`);
    console.log(`🔇 [RESPONSE] Stopping microphone to prevent echo`);
    
    // CRITICAL: Stop listening before AI speaks
    stopVoiceCall();
    setIsListening(false);
    
    setTranscript(responseText);
    setStatus('speaking');
    
    console.log(`🔊 [RESPONSE] Starting speech synthesis`);
    console.log('='.repeat(80) + '\n');
    
    // Play audio
    playVoiceResponse(responseText);
  };

  // Use voice hook
  const { startVoiceCall, stopVoiceCall, isRecording } = useVoiceAgent(
    sessionId,
    handleResponseReceived,
    setStatus
  );

  const playVoiceResponse = (text: string) => {
    console.log('\n' + '-'.repeat(80));
    console.log('🔊 [TTS] Starting Text-to-Speech');
    console.log('-'.repeat(80));
    
    isSpeakingRef.current = true;
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.volume = 1;
    
    utterance.onstart = () => {
      console.log('▶️ [TTS] Speech started');
      setStatus('speaking');
    };
    
    utterance.onend = () => {
      console.log('⏹️ [TTS] Speech ended');
      isSpeakingRef.current = false;
      console.log('-'.repeat(80));
      console.log('🎤 [LISTENING] Waiting 1 second before listening again...');
      console.log('-'.repeat(80) + '\n');
      
      // Wait 1 second after AI finishes speaking before listening again
      setTimeout(() => {
        console.log('\n' + '='.repeat(80));
        console.log('🎤 [LISTENING] Starting microphone');
        console.log('='.repeat(80));
        console.log('✅ [LISTENING] Ready to listen for user input');
        console.log('='.repeat(80) + '\n');
        
        setStatus('listening');
        setIsListening(true);
        startVoiceCall();
      }, 1000);
    };
    
    window.speechSynthesis.speak(utterance);
  };

  const handleStartCall = () => {
    console.log('\n' + '#'.repeat(80));
    console.log('📞 [CALL] START CALL BUTTON CLICKED');
    console.log('#'.repeat(80));
    console.log(`📋 [CALL] Session ID: ${sessionId}`);
    
    if (!sessionId) {
      console.error('❌ [CALL] No session ID available!');
      console.log('#'.repeat(80) + '\n');
      return;
    }
    
    console.log('✅ [CALL] Starting phone call...');
    console.log('#'.repeat(80) + '\n');
    
    setIsInCall(true);
    setTranscript('');
    setStatus('idle');
    
    // Wait a moment then greet
    setTimeout(() => {
      const greeting = `Hello! I'm your medical clinic AI assistant. I can help you with information about our services, book appointments, and answer health-related questions. How can I help you today?`;
      
      console.log('\n' + '='.repeat(80));
      console.log('👋 [GREETING] Playing initial greeting');
      console.log('='.repeat(80) + '\n');
      
      setTranscript(greeting);
      playVoiceResponse(greeting);
    }, 500);
  };

  const handleEndCall = () => {
    console.log('\n' + '!'.repeat(80));
    console.log('🛑 [EMERGENCY] EMERGENCY STOP: Killing conversation');
    console.log('!'.repeat(80));
    
    // Stop all voice processing
    stopVoiceCall();
    console.log('✅ [EMERGENCY] Voice call stopped');
    
    // Cancel any ongoing speech
    window.speechSynthesis.cancel();
    console.log('✅ [EMERGENCY] Speech synthesis cancelled');
    
    // Reset all states
    setIsInCall(false);
    setTranscript('');
    setStatus('idle');
    setIsListening(false);
    isSpeakingRef.current = false;
    
    console.log('✅ [EMERGENCY] All states reset');
    console.log('✅ [EMERGENCY] Conversation terminated');
    console.log('!'.repeat(80) + '\n');
  };

  const handleStopListening = () => {
    console.log('\n' + '■'.repeat(80));
    console.log('⏸️ [MANUAL STOP] User manually stopped listening');
    console.log('■'.repeat(80));
    
    stopVoiceCall();
    setIsListening(false);
    setStatus('thinking');
    
    console.log('✅ [MANUAL STOP] Voice recording stopped');
    console.log('🔄 [MANUAL STOP] Processing audio...');
    console.log('■'.repeat(80) + '\n');
  };

  return (
    <div className="app">
      <div className="container">
        {/* EMERGENCY KILL BUTTON - Always visible */}
        {isInCall && (
          <button 
            className="emergency-kill-btn"
            onClick={handleEndCall}
            title="Emergency Stop"
          >
            🛑
          </button>
        )}

        <header className="header">
          <div className="logo">
            <span className="icon">🏥</span>
            <h1>Medical Clinic</h1>
          </div>
          <p className="subtitle">AI Voice Assistant</p>
        </header>

        <main className="main">
          <div className="content">
            {!isInCall ? (
              // IDLE SCREEN - Just the button
              <div className="greeting">
                <h2>Welcome to Medical Clinic</h2>
                <p>Click to start a voice call</p>
                
                {/* Debug info */}
                {sessionError && (
                  <div style={{color: 'orange', fontSize: '12px', margin: '10px 0'}}>
                    ⚠️ Session warning: {sessionError}
                  </div>
                )}
                
                {sessionId && (
                  <div style={{color: 'green', fontSize: '12px', margin: '10px 0'}}>
                    ✅ Ready (Session: {sessionId.substring(0, 8)}...)
                  </div>
                )}
                
                <button
                  className="call-button"
                  onClick={handleStartCall}
                  disabled={!sessionId}
                >
                  ☎️ Call Clinic
                </button>
                
                {!sessionId && (
                  <p style={{color: 'gray', fontSize: '14px', marginTop: '10px'}}>
                    Initializing session...
                  </p>
                )}
              </div>
            ) : (
              // CALL SCREEN - Pure voice interface
              <div className="call-interface">
                {/* Header with status */}
                <div className="call-header">
                  <div className={`status-indicator ${status}`}>
                    <span className="status-dot"></span>
                    <span className="status-text">
                      {status === 'listening' && '🎤 Listening...'}
                      {status === 'thinking' && '⌛ Processing...'}
                      {status === 'speaking' && '🔊 Speaking...'}
                      {status === 'idle' && 'Ready to listen...'}
                      {status === 'error' && '❌ Error'}
                    </span>
                  </div>
                </div>

                {/* Main call area */}
                <div className="call-main">
                  {/* Waveform animation */}
                  <div className="waveform" style={{display: isRecording || isListening ? 'flex' : 'none'}}>
                    <div className="wave"></div>
                    <div className="wave"></div>
                    <div className="wave"></div>
                  </div>
                  
                  {/* Transcript display */}
                  <div className="transcript-display">
                    {transcript && (
                      <div className="transcript-text">
                        <p>{transcript}</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Footer - Buttons */}
                <div className="call-footer">
                  {/* Stop Listening Button (only when listening) */}
                  {isListening && (
                    <button 
                      className="btn-stop-listening"
                      onClick={handleStopListening}
                    >
                      <span>⏸️</span>
                      <span>Stop Listening</span>
                    </button>
                  )}
                  
                  <button 
                    className="btn-end-call"
                    onClick={handleEndCall}
                  >
                    ✕ End Call
                  </button>
                </div>
              </div>
            )}
          </div>
        </main>

        <footer className="footer">
          <p>Medical Clinic © 2025 | Powered by Voice AI</p>
        </footer>
      </div>
    </div>
  );
}

export default App;
