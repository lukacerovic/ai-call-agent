import React, { useState, useRef, useEffect } from 'react';
import '../styles/CallInterface.css';

interface CallState {
  isConnected: boolean;
  isListening: boolean;
  isSpeaking: boolean;
  status: string;
}

const CallInterface: React.FC = () => {
  const [callState, setCallState] = useState<CallState>({
    isConnected: false,
    isListening: false,
    isSpeaking: false,
    status: 'Ready to call',
  });

  const [transcripts, setTranscripts] = useState<Array<{ speaker: string; text: string }>>([]);
  const websocketRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const transcriptEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest transcript
  useEffect(() => {
    transcriptEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [transcripts]);

  const startCall = async () => {
    try {
      setCallState(prev => ({
        ...prev,
        status: 'Connecting to clinic...',
      }));

      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      // Initialize audio context
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      }

      // Connect to WebSocket
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.hostname}:8000/ws`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setCallState(prev => ({
          ...prev,
          isConnected: true,
          status: 'Listening to clinic agent...',
        }));
        startListening();
      };

      ws.onmessage = (event) => {
        if (event.data instanceof Blob) {
          // Handle audio response
          playAudio(event.data);
          setCallState(prev => ({
            ...prev,
            isSpeaking: true,
            status: 'Clinic agent speaking...',
          }));
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setCallState(prev => ({
          ...prev,
          status: 'Connection error. Please try again.',
        }));
      };

      ws.onclose = () => {
        setCallState(prev => ({
          ...prev,
          isConnected: false,
          isListening: false,
          status: 'Call ended',
        }));
      };

      websocketRef.current = ws;
    } catch (error) {
      console.error('Error starting call:', error);
      setCallState(prev => ({
        ...prev,
        status: 'Error: Microphone access denied',
      }));
    }
  };

  const startListening = () => {
    if (!streamRef.current || !websocketRef.current) return;

    setCallState(prev => ({
      ...prev,
      isListening: true,
    }));

    const audioContext = audioContextRef.current!;
    const source = audioContext.createMediaStreamSource(streamRef.current);
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 2048;
    source.connect(analyser);

    // Record audio
    const mediaRecorder = new MediaRecorder(streamRef.current);
    mediaRecorderRef.current = mediaRecorder;

    let audioChunks: BlobPart[] = [];
    let silenceCounter = 0;
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    const silenceThreshold = 30;
    const silenceDuration = 15; // 1.5 seconds at 100ms intervals

    const checkAudio = () => {
      analyser.getByteFrequencyData(dataArray);
      const average = dataArray.reduce((a, b) => a + b) / dataArray.length;

      if (average < silenceThreshold) {
        silenceCounter++;
      } else {
        silenceCounter = 0;
        if (!mediaRecorder.recording) {
          mediaRecorder.start();
        }
      }

      if (silenceCounter > silenceDuration && mediaRecorder.recording) {
        mediaRecorder.stop();
        silenceCounter = 0;
      }

      if (callState.isConnected) {
        requestAnimationFrame(checkAudio);
      }
    };

    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstop = () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
      audioChunks = [];

      // Send audio to backend
      if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
        websocketRef.current.send(audioBlob);
        // Transcribe locally for display
        transcribeAudio(audioBlob);
      }
    };

    checkAudio();
  };

  const transcribeAudio = async (audioBlob: Blob) => {
    // For demo purposes, show a placeholder
    // In production, you'd send to backend for transcription
    setTranscripts(prev => [...prev, {
      speaker: 'You',
      text: '[Listening to your speech...]',
    }]);
  };

  const playAudio = (audioBlob: Blob) => {
    const audio = new Audio(URL.createObjectURL(audioBlob));
    audio.play();

    audio.onended = () => {
      // Resume listening after agent speaks
      if (callState.isConnected) {
        setCallState(prev => ({
          ...prev,
          isSpeaking: false,
          status: 'Listening...',
        }));
        startListening();
      }
    };
  };

  const endCall = () => {
    if (websocketRef.current) {
      websocketRef.current.close();
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
    }
    setCallState(prev => ({
      ...prev,
      isConnected: false,
      isListening: false,
      isSpeaking: false,
      status: 'Call ended',
    }));
  };

  return (
    <div className="call-interface">
      <div className="clinic-header">
        <h1>☎️ AI Call Agent</h1>
        <p>Medical Clinic Voice Support System</p>
      </div>

      <div className="call-status">
        <div className={`status-indicator ${callState.isConnected ? 'connected' : ''}`}>
          <span className="status-dot"></span>
          <span className="status-text">{callState.status}</span>
        </div>
      </div>

      <div className="call-button-container">
        {!callState.isConnected ? (
          <button
            className="call-button call-btn"
            onClick={startCall}
            disabled={callState.isConnected}
          >
            📞 Call Clinic
          </button>
        ) : (
          <button
            className="call-button end-btn"
            onClick={endCall}
          >
            📵 End Call
          </button>
        )}
      </div>

      <div className="audio-indicator">
        {callState.isListening && (
          <div className="listening-animation">
            <div className="wave"></div>
            <div className="wave"></div>
            <div className="wave"></div>
            <p>Listening...</p>
          </div>
        )}
        {callState.isSpeaking && (
          <div className="speaking-animation">
            <div className="pulse"></div>
            <p>Agent Speaking...</p>
          </div>
        )}
      </div>

      {transcripts.length > 0 && (
        <div className="transcript-panel">
          <h3>Conversation</h3>
          <div className="transcript-content">
            {transcripts.map((transcript, idx) => (
              <div key={idx} className={`transcript-entry ${transcript.speaker.toLowerCase()}`}>
                <strong>{transcript.speaker}:</strong>
                <p>{transcript.text}</p>
              </div>
            ))}
            <div ref={transcriptEndRef} />
          </div>
        </div>
      )}

      <div className="info-panel">
        <h4>ℹ️ How to Use</h4>
        <ul>
          <li>Press "Call Clinic" to connect</li>
          <li>Speak naturally into your microphone</li>
          <li>Listen to the AI receptionist</li>
          <li>Press "End Call" to disconnect</li>
          <li>No text input needed - voice only!</li>
        </ul>
      </div>
    </div>
  );
};

export default CallInterface;
