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
  const [isProcessing, setIsProcessing] = useState(false);
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

        recognitionRef.current.continuous = true; // Changed back to true for natural speech with pauses
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
            setIsProcessing(true);
            onVoiceInput(finalTranscript.trim());
            // Stop listening after a short delay to feel more natural
            console.log('Final transcript sent, stopping recognition');
            setTimeout(() => {
              stopListening();
              setIsProcessing(false);
            }, 1000); // Increased delay for more natural feeling
            return;
          }

          // Reset timeout on speech activity
          if (timeoutRef.current) {
            clearTimeout(timeoutRef.current);
          }

          // Set a longer timeout for silence detection after speech activity
          timeoutRef.current = setTimeout(() => {
            console.log('5 seconds of silence detected, stopping recognition');
            stopListening();
          }, 5000); // Increased to 5 seconds of silence for more natural speech

          setErrorMsg('');
        };

        recognitionRef.current.onstart = () => {
          console.log('Speech recognition: service started');
          setErrorMsg('');
        };

        recognitionRef.current.onend = () => {
          console.log('Speech recognition: service ended');
          // Auto-stop when recognition ends naturally
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
    setIsProcessing(false);
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
        disabled={!isSupported || isProcessing}
        className={`p-4 rounded-2xl transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105 ${
          isProcessing
            ? 'bg-gradient-to-r from-yellow-500 to-orange-500 text-white animate-pulse'
            : isListening
            ? 'bg-gradient-to-r from-red-500 to-pink-500 text-white animate-pulse shadow-red-300'
            : 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white shadow-purple-300'
          } ${!isSupported || isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
        title={
          isProcessing 
            ? 'Processing voice input...'
            : isListening 
            ? 'Stop listening' 
            : 'Start voice input'
        }
      >
        {isProcessing ? (
          <div className="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
        ) : isListening ? (
          <MicOff className="h-5 w-5" />
        ) : (
          <Mic className="h-5 w-5" />
        )}
      </button>

      {/* Error Message Display */}
      {errorMsg && (
        <div className="bg-red-50 border border-red-300 rounded-2xl px-4 py-3 text-sm text-red-800 max-w-xs shadow-lg animate-fadeIn">
          <div className="flex items-center gap-2">
            <div className="text-red-500">⚠️</div>
            {errorMsg}
          </div>
        </div>
      )}

      {/* Transcript Display */}
      {transcript && (
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-2xl px-4 py-3 text-sm text-purple-800 max-w-xs shadow-lg animate-fadeIn">
          <div className="flex items-center gap-2">
            <span className="text-purple-500">🎤</span>
            <span>Recognized: </span>
            <span className="font-bold">{transcript}</span>
          </div>
        </div>
      )}

      {/* Status Indicator */}
      {isListening && (
        <div className="flex items-center gap-2 text-sm text-white bg-gradient-to-r from-purple-500 to-blue-500 px-4 py-2 rounded-2xl shadow-lg animate-fadeIn">
          <div className="w-3 h-3 bg-white rounded-full animate-pulse"></div>
          <span className="font-medium">Listening... 🎤</span>
        </div>
      )}
    </div>
  );
}