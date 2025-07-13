'use client';

import { useState, useEffect, useRef } from 'react';
import { Mic, MicOff } from 'lucide-react';

/* eslint-disable @typescript-eslint/no-explicit-any */

interface VoiceInterfaceProps {
  isListening: boolean;
  setIsListening: (listening: boolean) => void;
  onVoiceInput: (text: string) => void;
}

export default function VoiceInterface({ isListening, setIsListening, onVoiceInput }: VoiceInterfaceProps) {
  const [isSupported, setIsSupported] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const recognitionRef = useRef<any>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isInitializedRef = useRef(false);

  useEffect(() => {
    // Check if speech recognition is supported
    if (typeof window !== 'undefined' && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      setIsSupported(true);

      if (!isInitializedRef.current) {
        // Initialize speech recognition
        const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
        recognitionRef.current = new SpeechRecognition();

        recognitionRef.current.continuous = true;
        recognitionRef.current.interimResults = true;
        recognitionRef.current.lang = 'en-US';
        recognitionRef.current.maxAlternatives = 1;

        recognitionRef.current.onresult = (event: any) => {
          let finalTranscript = '';
          let interimTranscript = '';

          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              finalTranscript += transcript;
            } else {
              interimTranscript += transcript;
            }
          }

          const currentTranscript = finalTranscript || interimTranscript;
          setTranscript(currentTranscript);

          console.log('Voice recognition output:', currentTranscript);

          if (finalTranscript.trim()) {
            onVoiceInput(finalTranscript.trim());
          }

          // Reset timeout on speech activity
          if (timeoutRef.current) {
            clearTimeout(timeoutRef.current);
          }

          // Set a new timeout for silence detection after speech activity
          timeoutRef.current = setTimeout(() => {
            console.log('3 seconds of silence detected, stopping recognition');
            stopListening();
          }, 3000); // Stop after 3 seconds of silence

          setErrorMsg('');
        };

        recognitionRef.current.onstart = () => {
          console.log('Speech recognition: service started');
          setErrorMsg('');
        };

        recognitionRef.current.onend = () => {
          console.log('Speech recognition: service ended');
          // Don't auto-restart - user must click button to start again
          setIsListening(false);
          setTranscript('');
          clearTimeouts();
        };

        recognitionRef.current.onerror = (event: any) => {
          console.error('Speech recognition error:', event.error);
          let msg = 'Speech recognition error.';

          switch (event.error) {
            case 'not-allowed':
              msg = 'Microphone access denied. Please allow microphone permissions.';
              break;
            case 'no-speech':
              msg = 'No speech detected. Please try speaking.';
              // Don't stop on no-speech, just continue listening
              return;
            case 'audio-capture':
              msg = 'No microphone found. Please check your device.';
              break;
            case 'network':
              msg = 'Network error. Please check your connection.';
              break;
            case 'aborted':
              console.log('Recognition aborted - this is normal when stopping');
              return;
            default:
              msg = `Speech recognition error: ${event.error}`;
          }

          setErrorMsg(msg);
          setIsListening(false);
          setTranscript('');
          clearTimeouts();
        };

        // Optional: Add more event listeners for debugging
        recognitionRef.current.onaudiostart = () => console.log('Audio capturing started');
        recognitionRef.current.onaudioend = () => console.log('Audio capturing ended');
        recognitionRef.current.onsoundstart = () => console.log('Sound detected');
        recognitionRef.current.onsoundend = () => console.log('Sound ended');
        recognitionRef.current.onspeechstart = () => console.log('Speech detected');
        recognitionRef.current.onspeechend = () => console.log('Speech ended');

        isInitializedRef.current = true;
      }
    }

    return () => {
      clearTimeouts();
    };
  }, [onVoiceInput]);

  const clearTimeouts = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  };

  const startListening = () => {
    if (!isSupported) {
      alert('Speech recognition is not supported in your browser. Please use Chrome or Safari.');
      return;
    }

    try {
      setTranscript('');
      setErrorMsg('');
      clearTimeouts();

      console.log('Starting recognition');
      recognitionRef.current?.start();
      setIsListening(true);

      // ...no auto-stop timeout, only button will stop listening...

    } catch (error) {
      console.error('Failed to start recognition:', error);
      setErrorMsg('Failed to start speech recognition. Please try again.');
      setIsListening(false);
    }
  };

  const stopListening = () => {
    console.log('Stopping recognition');

    try {
      recognitionRef.current?.stop();
    } catch (error) {
      console.log('Recognition already stopped or error stopping:', error);
    }

    setIsListening(false);
    setTranscript('');
    setErrorMsg('');
    clearTimeouts();
  };

  const handleButtonClick = () => {
    console.log('Button clicked, current listening state:', isListening);

    if (isListening) {
      // If currently listening (red button), stop listening
      stopListening();
    } else {
      // If not listening (blue button), start listening
      startListening();
    }
  };

  return (
    <div className="flex items-center gap-2">
      {/* Voice Input Button */}
      <button
        onClick={handleButtonClick}
        disabled={!isSupported}
        className={`p-2 rounded-lg transition-all duration-200 ${isListening
            ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse'
            : 'bg-blue-500 hover:bg-blue-600 text-white'
          } ${!isSupported ? 'opacity-50 cursor-not-allowed' : ''}`}
        title={isListening ? 'Stop listening' : 'Start voice input'}
      >
        {isListening ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
      </button>

      {/* Error Message Display */}
      {errorMsg && (
        <div className="bg-red-100 border border-red-300 rounded-lg px-3 py-1 text-sm text-red-800 max-w-xs">
          {errorMsg}
        </div>
      )}

      {/* Transcript Display */}
      {transcript && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg px-3 py-1 text-sm text-blue-800 max-w-xs">
          <span>Recognized: </span>
          <span className="font-bold">{transcript}</span>
        </div>
      )}

      {/* Status Indicator */}
      {isListening && (
        <div className="flex items-center gap-1 text-sm text-blue-600 bg-blue-50 px-2 py-1 rounded-lg">
          <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
          <span className="font-medium">Listening... 🎤</span>
        </div>
      )}
    </div>
  );
}