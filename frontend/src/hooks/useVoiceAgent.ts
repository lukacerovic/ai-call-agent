import { useState, useRef, useCallback, useEffect } from 'react';

/**
 * Complete voice agent hook with client-side transcription
 * 
 * Flow:
 * 1. User speaks → Frontend captures audio
 * 2. Frontend VAD detects silence → Auto-stop recording
 * 3. Frontend transcribes audio (WebSpeech API or Whisper)
 * 4. Frontend sends text to backend AI
 * 5. Backend returns text response
 * 6. Frontend converts response to speech
 * 7. Loop continues
 */

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

interface UseVoiceAgentOptions {
  onMessage?: (message: Message) => void;
  onStateChange?: (state: string) => void;
}

export function useVoiceAgent(options: UseVoiceAgentOptions = {}) {
  // State
  const [state, setState] = useState<'idle' | 'listening' | 'processing' | 'speaking'>('idle');
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentTranscript, setCurrentTranscript] = useState('');
  const [sessionId, setSessionId] = useState<string>('');
  const [error, setError] = useState<string>('');

  // Refs
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const silenceTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const recognitionRef = useRef<any>(null);
  const synthRef = useRef<SpeechSynthesisUtterance | null>(null);
  const processingRef = useRef(false);

  // Constants
  const SILENCE_DURATION = 1500; // ms - wait this long after speech ends
  const MIN_SPEECH_DURATION = 500; // ms - ignore audio shorter than this
  const VAD_THRESHOLD = 0.02; // audio energy threshold

  /**
   * Update state with logging
   */
  const updateState = useCallback((newState: typeof state) => {
    console.log(`🔄 [STATE] ${state} → ${newState}`);
    setState(newState);
    options.onStateChange?.(newState);
  }, [state, options]);

  /**
   * Create new session with backend
   */
  const createSession = useCallback(async () => {
    try {
      console.log('📱 [SESSION] Creating new session...');
      const response = await fetch('http://localhost:8000/session/new', {
        method: 'GET',
      });
      const data = await response.json();
      setSessionId(data.session_id);
      console.log(`✅ [SESSION] Session created: ${data.session_id}`);
      return data.session_id;
    } catch (err) {
      const msg = `❌ [SESSION] Failed to create session: ${err}`;
      console.error(msg);
      setError(msg);
      throw err;
    }
  }, []);

  /**
   * Initialize microphone access
   */
  const initMicrophone = useCallback(async () => {
    try {
      console.log('🎤 [MIC] Requesting microphone access...');
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
      mediaStreamRef.current = stream;
      console.log('✅ [MIC] Microphone access granted');
      return stream;
    } catch (err) {
      const msg = `❌ [MIC] Microphone access denied: ${err}`;
      console.error(msg);
      setError(msg);
      throw err;
    }
  }, []);

  /**
   * Start recording audio
   */
  const startRecording = useCallback(async () => {
    try {
      let stream = mediaStreamRef.current;

      if (!stream) {
        stream = await initMicrophone();
      }

      audioChunksRef.current = [];

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus',
      });

      mediaRecorder.ondataavailable = (event: BlobEvent) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();

      console.log('🔴 [REC] Recording started');
      updateState('listening');

      return mediaRecorder;
    } catch (err) {
      console.error(`❌ [REC] Failed to start recording: ${err}`);
      throw err;
    }
  }, [initMicrophone, updateState]);

  /**
   * Stop recording and get audio blob
   */
  const stopRecording = useCallback((): Promise<Blob> => {
    return new Promise((resolve, reject) => {
      const mediaRecorder = mediaRecorderRef.current;

      if (!mediaRecorder) {
        reject(new Error('MediaRecorder not initialized'));
        return;
      }

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: 'audio/webm;codecs=opus',
        });
        console.log(`⏹️  [REC] Recording stopped (${audioBlob.size} bytes)`);
        resolve(audioBlob);
      };

      mediaRecorder.stop();
    });
  }, []);

  /**
   * Transcribe audio using Web Speech API
   */
  const transcribeAudio = useCallback(
    async (audioBlob: Blob): Promise<string> => {
      try {
        console.log('\n' + '='.repeat(80));
        console.log('📝 [TRANSCRIBE] Starting transcription...');
        console.log('='.repeat(80));

        // Use Web Speech API (built-in, no server needed)
        return new Promise((resolve, reject) => {
          // Use SpeechRecognition from browser
          const SpeechRecognition =
            window.SpeechRecognition || (window as any).webkitSpeechRecognition;

          if (!SpeechRecognition) {
            const msg = '❌ [TRANSCRIBE] Speech Recognition API not supported';
            console.error(msg);
            reject(new Error(msg));
            return;
          }

          const recognition = new SpeechRecognition();
          recognition.continuous = false;
          recognition.interimResults = false;
          recognition.lang = 'en-US';

          let isFinal = false;
          let transcript = '';

          recognition.onstart = () => {
            console.log('🎤 [TRANSCRIBE] Recognition started');
          };

          recognition.onresult = (event: any) => {
            for (let i = event.resultIndex; i < event.results.length; i++) {
              const transcriptPart = event.results[i][0].transcript;
              isFinal = event.results[i].isFinal;
              transcript += transcriptPart + ' ';
            }

            const status = isFinal ? '✅ FINAL' : '⏳ interim';
            console.log(`📝 [TRANSCRIBE] ${status}: "${transcript.trim()}"`);
          };

          recognition.onerror = (event: any) => {
            console.error(`❌ [TRANSCRIBE] Error: ${event.error}`);
            reject(new Error(`Speech recognition error: ${event.error}`));
          };

          recognition.onend = () => {
            console.log('🔇 [TRANSCRIBE] Recognition ended');
            if (transcript.trim()) {
              console.log(`\n✅ [TRANSCRIBE] Final transcription: "${transcript.trim()}"`);
              console.log('='.repeat(80) + '\n');
              resolve(transcript.trim());
            } else {
              const msg = '⚠️  [TRANSCRIBE] Empty transcription';
              console.warn(msg);
              reject(new Error(msg));
            }
          };

          // Use AudioContext to create audio stream from blob
          const audioContext = new (window.AudioContext ||
            (window as any).webkitAudioContext)();
          const reader = new FileReader();

          reader.onload = async (e) => {
            try {
              const arrayBuffer = e.target?.result as ArrayBuffer;
              const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

              // Create oscillator to "simulate" audio (Web Speech API works differently)
              // Actually, we need to use the audio blob directly via URL
              const url = URL.createObjectURL(audioBlob);
              const audio = new Audio(url);
              audio.play();

              // Start recognition
              recognition.start();
            } catch (err) {
              console.error('Failed to decode audio:', err);
              // Fall back to direct recognition
              recognition.start();
            }
          };

          reader.readAsArrayBuffer(audioBlob);
        });
      } catch (err) {
        console.error(`❌ [TRANSCRIBE] Error: ${err}`);
        throw err;
      }
    },
    []
  );

  /**
   * Send text message to AI backend
   */
  const sendMessage = useCallback(
    async (text: string) => {
      if (!sessionId) {
        console.error('❌ [CHAT] No session ID');
        return null;
      }

      try {
        updateState('processing');
        console.log('\n' + '='.repeat(80));
        console.log(`💬 [CHAT] Sending message to AI: "${text}"`);
        console.log('='.repeat(80));

        const response = await fetch('http://localhost:8000/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_id: sessionId,
            message: text,
          }),
        });

        const data = await response.json();
        const aiResponse = data.response;

        console.log(`\n✅ [CHAT] AI Response: "${aiResponse}"`);
        console.log('='.repeat(80) + '\n');

        return aiResponse;
      } catch (err) {
        const msg = `❌ [CHAT] Failed to send message: ${err}`;
        console.error(msg);
        setError(msg);
        return null;
      }
    },
    [sessionId, updateState]
  );

  /**
   * Convert text to speech
   */
  const speakText = useCallback(async (text: string) => {
    try {
      updateState('speaking');
      console.log('\n' + '='.repeat(80));
      console.log(`🔊 [TTS] Speaking: "${text}"`);
      console.log('='.repeat(80));

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1;
      utterance.pitch = 1;
      utterance.volume = 1;

      return new Promise((resolve) => {
        utterance.onend = () => {
          console.log('✅ [TTS] Speech finished');
          console.log('='.repeat(80) + '\n');
          updateState('idle');
          resolve(true);
        };

        utterance.onerror = (err) => {
          console.error(`❌ [TTS] Error: ${err}`);
          updateState('idle');
          resolve(false);
        };

        window.speechSynthesis.speak(utterance);
      });
    } catch (err) {
      console.error(`❌ [TTS] Error: ${err}`);
      updateState('idle');
      return false;
    }
  }, [updateState]);

  /**
   * Complete conversation cycle
   */
  const startConversation = useCallback(async () => {
    try {
      console.log('\n' + '━'.repeat(80));
      console.log('🎯 [CYCLE] Starting new conversation cycle');
      console.log('━'.repeat(80) + '\n');

      processingRef.current = true;

      // 1. Start recording
      await startRecording();

      // 2. Wait for silence to stop recording
      let lastSoundTime = Date.now();
      const audioContext = new (window.AudioContext ||
        (window as any).webkitAudioContext)();
      const analyser = audioContext.createAnalyser();
      const source = audioContext.createMediaStreamSource(
        mediaStreamRef.current!
      );
      source.connect(analyser);

      const dataArray = new Uint8Array(analyser.frequencyBinCount);

      const checkSilence = () => {
        analyser.getByteFrequencyData(dataArray);
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length;

        if (average > VAD_THRESHOLD * 255) {
          // Sound detected
          lastSoundTime = Date.now();
          console.log(`🔊 [VAD] Sound detected (level: ${average.toFixed(0)})`);
        } else if (Date.now() - lastSoundTime > SILENCE_DURATION) {
          // Silence detected for long enough
          console.log(`⏸️  [VAD] Silence detected - stopping recording!`);
          stopRecording().then((audioBlob) => {
            // 3. Transcribe
            transcribeAudio(audioBlob).then((transcript) => {
              // 4. Send to AI
              sendMessage(transcript).then(async (aiResponse) => {
                if (aiResponse) {
                  // 5. Speak response
                  await speakText(aiResponse);
                  // 6. Loop
                  processingRef.current = false;
                  startConversation();
                }
              });
            });
          });
          clearInterval(silenceCheckInterval);
        }
      };

      const silenceCheckInterval = setInterval(checkSilence, 100);
    } catch (err) {
      console.error(`❌ [CYCLE] Error: ${err}`);
      processingRef.current = false;
    }
  }, [startRecording, stopRecording, transcribeAudio, sendMessage, speakText]);

  /**
   * Initialize on mount
   */
  const initialize = useCallback(async () => {
    try {
      console.log('\n' + '═'.repeat(80));
      console.log('🚀 [INIT] Initializing Voice Agent');
      console.log('═'.repeat(80) + '\n');

      const newSessionId = await createSession();
      await initMicrophone();

      console.log('✅ [INIT] Voice Agent ready!');
      console.log('═'.repeat(80) + '\n');

      updateState('idle');
      return true;
    } catch (err) {
      console.error(`❌ [INIT] Initialization failed: ${err}`);
      return false;
    }
  }, [createSession, initMicrophone, updateState]);

  /**
   * Cleanup
   */
  useEffect(() => {
    return () => {
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      }
      if (silenceTimeoutRef.current) {
        clearTimeout(silenceTimeoutRef.current);
      }
    };
  }, []);

  return {
    state,
    messages,
    currentTranscript,
    sessionId,
    error,
    initialize,
    startConversation,
    stopRecording,
  };
}
