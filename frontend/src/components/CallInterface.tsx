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
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const silenceCounterRef = useRef<number>(0);
  const isRecordingRef = useRef<boolean>(false);

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
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: false,
          sampleRate: 16000,
        } 
      });
      streamRef.current = stream;
      console.log('✅ Microphone access granted');

      // Initialize audio context
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      }

      // Connect to WebSocket
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.hostname}:8000/ws`;
      console.log(`📡 Connecting to WebSocket: ${wsUrl}`);
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('✅ WebSocket connected');
        setCallState(prev => ({
          ...prev,
          isConnected: true,
          status: 'Connected. Listening to clinic agent greeting...',
        }));
      };

      ws.onmessage = (event) => {
        console.log(`📥 Received from backend: ${event.data.byteLength || event.data.length} bytes`);
        if (event.data instanceof Blob) {
          // Handle audio response
          playAudio(event.data);
          setCallState(prev => ({
            ...prev,
            isSpeaking: true,
            isListening: false,
            status: 'Clinic agent speaking...',
          }));
        }
      };

      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        setCallState(prev => ({
          ...prev,
          status: 'Connection error. Please try again.',
        }));
      };

      ws.onclose = () => {
        console.log('🔌 WebSocket disconnected');
        setCallState(prev => ({
          ...prev,
          isConnected: false,
          isListening: false,
          status: 'Call ended',
        }));
        stopListening();
      };

      websocketRef.current = ws;
    } catch (error) {
      console.error('❌ Error starting call:', error);
      setCallState(prev => ({
        ...prev,
        status: 'Error: Microphone access denied',
      }));
    }
  };

  const startListening = () => {
    if (!streamRef.current || !websocketRef.current) {
      console.error('❌ Stream or WebSocket not available');
      return;
    }

    console.log('🎤 Starting voice capture...');
    setCallState(prev => ({
      ...prev,
      isListening: true,
      status: 'Listening...',
    }));

    const audioContext = audioContextRef.current!;
    const source = audioContext.createMediaStreamSource(streamRef.current);
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 2048;
    analyserRef.current = analyser;
    source.connect(analyser);

    // Create MediaRecorder for continuous recording
    const mediaRecorder = new MediaRecorder(streamRef.current, {
      mimeType: 'audio/webm',
    });
    mediaRecorderRef.current = mediaRecorder;

    let audioChunks: BlobPart[] = [];
    silenceCounterRef.current = 0;
    isRecordingRef.current = false;

    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    const silenceThreshold = 25; // Lower threshold for better detection
    const silenceDurationFrames = 15; // ~1.5 seconds at 100ms intervals

    // Monitor audio levels and manage recording
    const checkAudio = () => {
      if (!callState.isConnected) {
        console.log('📵 Call disconnected, stopping audio check');
        return;
      }

      analyser.getByteFrequencyData(dataArray);
      const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
      const isSpeechDetected = average > silenceThreshold;

      if (isSpeechDetected) {
        silenceCounterRef.current = 0;
        // Start recording if not already recording
        if (!isRecordingRef.current) {
          console.log('🔴 Speech detected, starting recording');
          audioChunks = [];
          mediaRecorder.start();
          isRecordingRef.current = true;
        }
      } else {
        // Increment silence counter
        if (isRecordingRef.current) {
          silenceCounterRef.current++;
          console.log(`🔇 Silence detected (${silenceCounterRef.current}/${silenceDurationFrames})`);
        }
      }

      // If silence threshold reached and was recording, stop and send
      if (silenceCounterRef.current >= silenceDurationFrames && isRecordingRef.current) {
        console.log('⏹️ Silence duration reached, stopping recording and sending');
        mediaRecorder.stop();
        isRecordingRef.current = false;
        silenceCounterRef.current = 0;
      }

      animationFrameRef.current = requestAnimationFrame(checkAudio);
    };

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        console.log(`📝 Audio chunk received: ${event.data.size} bytes`);
        audioChunks.push(event.data);
      }
    };

    mediaRecorder.onstop = () => {
      if (audioChunks.length > 0) {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        console.log(`📦 Compiled audio blob: ${audioBlob.size} bytes`);

        // Send audio to backend
        if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
          console.log(`📤 Sending audio to backend: ${audioBlob.size} bytes`);
          websocketRef.current.send(audioBlob);
          
          // Show user's speech as [Processing...]
          setTranscripts(prev => [...prev, {
            speaker: 'You',
            text: '[Processing your speech...]',
          }]);
        } else {
          console.error('❌ WebSocket not open, cannot send audio');
        }
        audioChunks = [];
      }
    };

    // Start the audio monitoring loop
    checkAudio();
  };

  const stopListening = () => {
    console.log('🛑 Stopping audio capture');
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
    if (mediaRecorderRef.current && isRecordingRef.current) {
      mediaRecorderRef.current.stop();
      isRecordingRef.current = false;
    }
  };

  const playAudio = (audioBlob: Blob) => {
    console.log(`🔊 Playing audio: ${audioBlob.size} bytes`);
    const audio = new Audio(URL.createObjectURL(audioBlob));
    
    audio.onplay = () => {
      console.log('▶️ Audio started playing');
    };
    
    audio.onended = () => {
      console.log('⏹️ Audio finished playing');
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
    
    audio.onerror = (error) => {
      console.error('❌ Audio playback error:', error);
    };
    
    audio.play().catch(error => {
      console.error('❌ Failed to play audio:', error);
    });
  };

  const endCall = () => {
    console.log('📵 Ending call');
    stopListening();
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
            ☎️ Call Clinic
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
          <li>Press "☎️ Call Clinic" to connect</li>
          <li>Listen to the AI receptionist greeting</li>
          <li>Speak naturally into your microphone</li>
          <li>Pause for 2-3 seconds when done speaking (signals end of message)</li>
          <li>Listen to the AI response</li>
          <li>Continue the conversation naturally</li>
          <li>Press "📵 End Call" to disconnect</li>
          <li>No text input needed - voice only!</li>
        </ul>
      </div>
    </div>
  );
};

export default CallInterface;
