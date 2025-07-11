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
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    // Check if speech recognition is supported
    if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
      setIsSupported(true);
      
      // Initialize speech recognition
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

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

        setTranscript(finalTranscript || interimTranscript);
        
        if (finalTranscript) {
          onVoiceInput(finalTranscript);
          setTranscript('');
        }
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [onVoiceInput, setIsListening]);

  const toggleListening = () => {
    if (!isSupported) {
      alert('Speech recognition is not supported in your browser. Please use Chrome or Safari.');
      return;
    }

    if (isListening) {
      try {
        recognitionRef.current?.stop();
      } catch {
        console.log('Recognition already stopped');
      }
      setIsListening(false);
    } else {
      try {
        setTranscript('');
        recognitionRef.current?.start();
        setIsListening(true);
      } catch (error) {
        console.error('Failed to start recognition:', error);
        setIsListening(false);
      }
    }
  };



  return (
    <div className="flex items-center gap-2">
      {/* Voice Input Button */}
      <button
        onClick={toggleListening}
        disabled={!isSupported}
        className={`p-2 rounded-lg transition-all duration-200 ${
          isListening
            ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse'
            : 'bg-blue-500 hover:bg-blue-600 text-white'
        } ${!isSupported ? 'opacity-50 cursor-not-allowed' : ''}`}
        title={isListening ? 'Stop listening' : 'Start voice input'}
      >
        {isListening ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
      </button>

      {/* Transcript Display */}
      {transcript && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg px-3 py-1 text-sm text-blue-800 max-w-xs">
          {transcript}
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