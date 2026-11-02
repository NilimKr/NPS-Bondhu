import React, { useState, useRef, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Send, Loader2, Mic, MicOff, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import MessageBubble from './MessageBubble';

const WELCOME = {
    en: "Namaste! I am NPS Bondhu. I can help you understand your pension benefits, tax savings, or guide you through the exit process. What's on your mind today?",
    hi: 'नमस्ते! मैं NPS बंधु हूं। मैं आपकी पेंशन लाभ, कर बचत, या बाहर निकलने की प्रक्रिया के बारे में मदद कर सकता हूं। आज आप क्या जानना चाहते हैं?',
    as: "নমস্কাৰ! মই NPS বন্ধু। মই আপোনাৰ পেঞ্চন সুবিধা, কৰ সঞ্চয়, বা প্ৰস্থান প্ৰক্ৰিয়াৰ বিষয়ে সহায় কৰিব পাৰোঁ। আজি আপোনাৰ মনত কি আছে?",
};

const PLACEHOLDERS = {
    en: 'Ask about tax, withdrawal, or PRAN...',
    hi: 'कर, निकासी, या PRAN के बारे में पूछें...',
    as: 'কৰ, উলিওৱা, বা PRAN ৰ বিষয়ে সোধক...',
};

const CHIPS = {
    en: ['Exit Rules', 'Tier II Account', 'Annuity Rates', 'Tax Benefits', 'PRAN Status'],
    hi: ['निकासी नियम', 'टियर II खाता', 'वार्षिकी दरें', 'कर लाभ', 'PRAN स्थिति'],
    as: ['প্ৰস্থান নিয়ম', 'টায়াৰ II একাউণ্ট', 'বাৰ্ষিক হাৰ', 'কৰ সুবিধা', 'PRAN স্থিতি'],
};

// BCP-47 language tags for Web Speech API
const SPEECH_LANG = {
    en: 'en-IN',
    hi: 'hi-IN',
    as: 'as-IN',
};

const ChatInterface = ({ language }) => {
    const [messages, setMessages] = useState([
        {
            role: 'assistant',
            content: WELCOME[language] || WELCOME['en'],
            timestamp: new Date(),
        },
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isListening, setIsListening] = useState(false);
    const [isTranscribing, setIsTranscribing] = useState(false);
    const [voiceNotice, setVoiceNotice] = useState(null);
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);
    const recognitionRef = useRef(null);
    const silenceTimerRef = useRef(null);
    const mediaRecorderRef = useRef(null);
    const audioStreamRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]);

    useEffect(() => {
        if (messages.length === 1 && messages[0].role === 'assistant') {
            setMessages([
                {
                    role: 'assistant',
                    content: WELCOME[language] || WELCOME['en'],
                    timestamp: new Date(),
                },
            ]);
        }
    }, [language]);

    // Clean up speech recognition and timers on unmount or language change
    useEffect(() => {
        return () => {
            if (silenceTimerRef.current) {
                clearTimeout(silenceTimerRef.current);
                silenceTimerRef.current = null;
            }
            if (recognitionRef.current) {
                recognitionRef.current.abort();
                recognitionRef.current = null;
            }
            if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
                try { mediaRecorderRef.current.stop(); } catch (e) {}
                mediaRecorderRef.current = null;
            }
            if (audioStreamRef.current) {
                audioStreamRef.current.getTracks().forEach((t) => t.stop());
                audioStreamRef.current = null;
            }
        };
    }, [language]);

    const stopVoiceInput = useCallback(() => {
        if (silenceTimerRef.current) {
            clearTimeout(silenceTimerRef.current);
            silenceTimerRef.current = null;
        }
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
            try {
                mediaRecorderRef.current.stop();
            } catch (e) {}
        }
        setIsListening(false);
    }, []);

    // ---------- Unified Whisper Audio Recording for Assamese, Hindi & English ----------
    const startWhisperRecording = useCallback(async (targetLang = 'as') => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            audioStreamRef.current = stream;

            const audioChunks = [];
            let mimeType = '';
            let fileExt = 'webm';

            if (typeof MediaRecorder !== 'undefined') {
                if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
                    mimeType = 'audio/webm;codecs=opus';
                    fileExt = 'webm';
                } else if (MediaRecorder.isTypeSupported('audio/webm')) {
                    mimeType = 'audio/webm';
                    fileExt = 'webm';
                } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
                    mimeType = 'audio/mp4';
                    fileExt = 'mp4';
                } else if (MediaRecorder.isTypeSupported('audio/aac')) {
                    mimeType = 'audio/aac';
                    fileExt = 'aac';
                }
            }

            const mediaRecorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;

            let audioCtx = null;
            let checkInterval = null;
            let hasSpoken = false;
            let silenceStartTime = null;

            // Optional Voice Activity Detection (VAD) for auto-stop after user finishes speaking
            try {
                const AudioCtxClass = window.AudioContext || window.webkitAudioContext;
                if (AudioCtxClass) {
                    audioCtx = new AudioCtxClass();
                    if (audioCtx.state === 'suspended') {
                        audioCtx.resume().catch(() => {});
                    }
                    const source = audioCtx.createMediaStreamSource(stream);
                    const analyser = audioCtx.createAnalyser();
                    analyser.fftSize = 512;
                    source.connect(analyser);

                    const timeData = new Uint8Array(analyser.fftSize);
                    checkInterval = setInterval(() => {
                        try {
                            analyser.getByteTimeDomainData(timeData);
                            let maxDev = 0;
                            for (let i = 0; i < timeData.length; i++) {
                                const dev = Math.abs(timeData[i] - 128);
                                if (dev > maxDev) maxDev = dev;
                            }

                            if (maxDev > 8) {
                                hasSpoken = true;
                                silenceStartTime = null;
                            } else if (hasSpoken) {
                                if (!silenceStartTime) {
                                    silenceStartTime = Date.now();
                                } else if (Date.now() - silenceStartTime > 1600) {
                                    // Auto-stop after 1.6s pause following speech
                                    if (mediaRecorder.state === 'recording') {
                                        mediaRecorder.stop();
                                    }
                                }
                            }
                        } catch (e) {}
                    }, 100);
                }
            } catch (e) {
                console.warn('VAD unavailable, relying on manual stop / timeout:', e);
            }

            const existingText = input;

            mediaRecorder.ondataavailable = (e) => {
                if (e.data && e.data.size > 0) {
                    audioChunks.push(e.data);
                }
            };

            mediaRecorder.onstart = () => {
                setIsListening(true);
                const noticeMsg = targetLang === 'as'
                    ? '🎙️ শুনি আছোঁ... (কওক, শেষ হ’লে মাইকত ক্লিক কৰক)'
                    : targetLang === 'hi'
                    ? '🎙️ सुन रहा हूँ... (बोलें, पूरा होने पर माइक पर क्लिक करें)'
                    : '🎙️ Listening... (Speak now, click mic when done)';

                setVoiceNotice({
                    type: 'info',
                    msg: noticeMsg
                });

                // Auto stop after 9 seconds of recording
                silenceTimerRef.current = setTimeout(() => {
                    if (mediaRecorder.state === 'recording') {
                        mediaRecorder.stop();
                    }
                }, 9000);
            };

            mediaRecorder.onstop = async () => {
                if (checkInterval) clearInterval(checkInterval);
                if (silenceTimerRef.current) {
                    clearTimeout(silenceTimerRef.current);
                    silenceTimerRef.current = null;
                }
                stream.getTracks().forEach((track) => track.stop());
                try { audioCtx?.close(); } catch (e) {}
                setIsListening(false);

                if (audioChunks.length === 0) {
                    setVoiceNotice(null);
                    return;
                }

                const actualMime = mediaRecorder.mimeType || mimeType || 'audio/webm';
                const blob = new Blob(audioChunks, { type: actualMime });

                if (blob.size < 400) {
                    setVoiceNotice({
                        type: 'info',
                        msg: targetLang === 'as'
                            ? 'ৰেৰ্কডিং অতি চুটি হ’ল। অনুগ্ৰহ কৰি আকৌ কওক।'
                            : 'Recording too short. Please try again.'
                    });
                    setTimeout(() => setVoiceNotice(null), 3000);
                    return;
                }

                setIsTranscribing(true);
                setVoiceNotice({
                    type: 'info',
                    msg: targetLang === 'as'
                        ? 'মাত প্ৰক্ৰিয়াকৰণ কৰা হৈছে...'
                        : 'Transcribing speech with Whisper...'
                });

                try {
                    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
                    const formData = new FormData();
                    formData.append('file', blob, `recording.${fileExt}`);
                    formData.append('language', targetLang);

                    const response = await axios.post(`${apiBaseUrl}/transcribe`, formData, {
                        headers: { 'Content-Type': 'multipart/form-data' },
                    });

                    if (response.data && response.data.text && response.data.text.trim()) {
                        const transcribed = response.data.text.trim();
                        const prefix = existingText ? existingText + ' ' : '';
                        setInput(prefix + transcribed);
                        setVoiceNotice(null);
                    } else {
                        setVoiceNotice({
                            type: 'info',
                            msg: targetLang === 'as'
                                ? 'কোনো মাত স্পষ্টকৈ ধৰিব পৰা নগ’ল। অনুগ্ৰহ কৰি মাইকৰ ওচৰত কওক।'
                                : targetLang === 'hi'
                                ? 'आवाज़ स्पष्ट नहीं थी। कृपया माइक के पास साफ़ बोलें।'
                                : 'Could not recognize speech clearly. Please speak closer to your mic.'
                        });
                        setTimeout(() => setVoiceNotice(null), 3500);
                    }
                } catch (err) {
                    console.error('Transcription error:', err);
                    setVoiceNotice({
                        type: 'error',
                        msg: 'Voice transcription failed. Please try speaking again or type your question.'
                    });
                    setTimeout(() => setVoiceNotice(null), 3500);
                } finally {
                    setIsTranscribing(false);
                    inputRef.current?.focus();
                }
            };

            mediaRecorder.start(250);
        } catch (err) {
            console.error('Microphone error:', err);
            setIsListening(false);
            setVoiceNotice({
                type: 'error',
                msg: 'Microphone permission denied. Please allow microphone access in your browser.'
            });
            setTimeout(() => setVoiceNotice(null), 4000);
        }
    }, [input]);

    // ---------- Voice Input Logic ----------
    const toggleVoiceInput = useCallback(() => {
        // If already listening or transcribing, stop immediately
        if (isListening || isTranscribing) {
            stopVoiceInput();
            return;
        }

        setVoiceNotice(null);
        startWhisperRecording(language);
    }, [isListening, isTranscribing, language, stopVoiceInput, startWhisperRecording]);

    const sendMessage = async (text) => {
        if (!text.trim() || isLoading) return;

        // Stop listening if active
        stopVoiceInput();

        const userMessage = { role: 'user', content: text.trim(), timestamp: new Date() };
        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
            if (!apiBaseUrl) {
                throw new Error('VITE_API_BASE_URL is not configured. Add it to your Vercel environment variables.');
            }
            const response = await axios.post(`${apiBaseUrl}/chat`, {
                message: userMessage.content,
                language: language,
            });

            const botMessage = {
                role: 'assistant',
                content: response.data.answer,
                sources: response.data.sources,
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, botMessage]);
        } catch (error) {
            console.error('Error:', error);
            // Check if it's a timeout / network error (Render free tier cold start)
            const isTimeout = error.code === 'ECONNABORTED' || error.message?.includes('timeout') || error.message?.includes('Network Error');
            const errMsgs = isTimeout
                ? {
                    en: 'The server is waking up — this can take 30–60 seconds on the first request. Please try again in a moment!',
                    hi: 'सर्वर जाग रहा है — पहले अनुरोध में 30-60 सेकंड लग सकते हैं। कृपया थोड़ी देर में पुनः प्रयास करें!',
                    as: 'চাৰ্ভাৰটো জাগি উঠিছে — প্ৰথম অনুৰোধত ৩০–৬০ ছেকেণ্ড লাগিব পাৰে। অনুগ্ৰহ কৰি অলপ পিছত পুনৰাই চেষ্টা কৰক!',
                }
                : {
                    en: 'Sorry, I encountered an error. Please try again.',
                    hi: 'क्षमा करें, एक त्रुटि हुई। कृपया पुनः प्रयास करें।',
                    as: 'দুঃখিত, এটা ত্ৰুটি হৈছে। অনুগ্ৰহ কৰি পুনৰাই চেষ্টা কৰক।',
                };
            setMessages((prev) => [
                ...prev,
                { role: 'assistant', content: errMsgs[language] || errMsgs['en'], isError: true, timestamp: new Date() },
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        sendMessage(input);
    };

    const showWelcome = messages.length <= 1;

    return (
        <div className="flex-1 flex flex-col h-full bg-gradient-to-b from-blue-50/40 via-slate-50 to-slate-50 relative overflow-hidden">
            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto px-4 md:px-6 pt-4 md:pt-6 pb-44">
                <div className="max-w-2xl mx-auto w-full">

                    {/* ── Elegant Welcome Banner ── */}
                    {showWelcome && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6, ease: 'easeOut' }}
                            className="text-center pt-8 pb-8 mb-4"
                        >
                            <motion.div
                                initial={{ scale: 0.85, opacity: 0 }}
                                animate={{ scale: 1, opacity: 1 }}
                                transition={{ duration: 0.4, delay: 0.15 }}
                                className="inline-flex items-center justify-center w-24 h-24 mb-4"
                            >
                                <img
                                    src="/nps-logo.svg"
                                    alt="NPS Bondhu Logo"
                                    className="w-full h-full object-contain drop-shadow-sm"
                                />
                            </motion.div>
                            <motion.h1
                                initial={{ opacity: 0, y: 8 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.4, delay: 0.3 }}
                                className="text-2xl md:text-[28px] font-bold text-slate-800 tracking-tight mb-2"
                            >
                                Welcome to NPS Bondhu
                            </motion.h1>
                            <motion.p
                                initial={{ opacity: 0, y: 6 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.4, delay: 0.45 }}
                                className="text-sm md:text-[15px] text-slate-500 leading-relaxed mb-1.5"
                            >
                                Your AI-Powered Guide to the National Pension System
                            </motion.p>
                            <motion.p
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                transition={{ duration: 0.4, delay: 0.6 }}
                                className="text-xs text-blue-400/60 font-medium tracking-wide"
                            >
                                Powered by Official NPS Documents
                            </motion.p>
                        </motion.div>
                    )}

                    {/* Messages */}
                    <AnimatePresence initial={false}>
                        {messages.map((msg, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.25, delay: index === 0 ? 0.15 : 0 }}
                            >
                                <MessageBubble message={msg} />
                            </motion.div>
                        ))}
                    </AnimatePresence>

                    {/* Typing indicator */}
                    {isLoading && (
                        <motion.div
                            initial={{ opacity: 0, y: 8 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="flex items-start gap-2.5 mb-4"
                        >
                            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-500 flex items-center justify-center mt-1 shadow-sm">
                                <Loader2 size={14} className="text-white animate-spin" />
                            </div>
                            <div className="bg-white border border-slate-200/80 rounded-2xl rounded-tl-md px-5 py-3.5 shadow-sm">
                                <div className="flex items-center gap-1.5">
                                    <div className="w-2 h-2 rounded-full bg-slate-400 typing-dot" />
                                    <div className="w-2 h-2 rounded-full bg-slate-300 typing-dot" />
                                    <div className="w-2 h-2 rounded-full bg-slate-200 typing-dot" />
                                </div>
                            </div>
                        </motion.div>
                    )}

                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Bottom Bar: Chips + Input */}
            <div className="absolute bottom-0 left-0 w-full bg-white border-t border-slate-100 shadow-[0_-4px_20px_rgba(0,0,0,0.04)]">
                {/* Quick Chips — scrollable row */}
                <div className="overflow-x-auto no-scrollbar">
                    <div className="flex items-center gap-2 px-4 md:px-6 pt-3 pb-2 max-w-2xl mx-auto">
                        {(CHIPS[language] || CHIPS['en']).map((chip, i) => (
                            <button
                                key={i}
                                onClick={() => sendMessage(chip)}
                                disabled={isLoading}
                                className="flex-shrink-0 px-3.5 py-1.5 rounded-full text-[12px] font-medium
                  bg-white/80 border border-blue-100/60 text-slate-500
                  hover:border-blue-300 hover:text-blue-600 hover:bg-blue-50/60
                  hover:-translate-y-0.5 hover:shadow-sm hover:shadow-blue-100/40
                  active:scale-95 transition-all duration-200
                  disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:translate-y-0"
                            >
                                {chip}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Voice Input Notice / Fallback Banner */}
                {voiceNotice && (
                    <div className="max-w-2xl mx-auto px-4 md:px-6 pb-2">
                        <div className={`text-[12px] px-3 py-1.5 rounded-xl border flex items-center justify-between shadow-sm animate-fade-in ${
                            typeof voiceNotice === 'object' && voiceNotice?.type === 'error'
                                ? 'bg-rose-50/90 border-rose-200/80 text-rose-700'
                                : 'bg-blue-50/90 border-blue-200/80 text-blue-700'
                        }`}>
                            <span>{typeof voiceNotice === 'object' ? voiceNotice?.msg : String(voiceNotice)}</span>
                            <button
                                type="button"
                                onClick={() => setVoiceNotice(null)}
                                className="ml-2 text-slate-400 hover:text-slate-700 font-bold text-sm leading-none"
                            >
                                ×
                            </button>
                        </div>
                    </div>
                )}

                {/* Input */}
                <div className="px-4 md:px-6 pb-4">
                    <div className="max-w-2xl mx-auto">
                        <form onSubmit={handleSubmit} className="flex items-center gap-2">
                            <div className="relative flex-1">
                                <input
                                    ref={inputRef}
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    placeholder={PLACEHOLDERS[language] || PLACEHOLDERS['en']}
                                    className="w-full pl-4 pr-10 py-3 bg-blue-50/40 border border-blue-100/50 rounded-full
                    focus:outline-none focus:bg-white focus:border-blue-400 focus:ring-2 focus:ring-blue-100
                    hover:border-blue-200/70 transition-all duration-200 text-sm text-slate-700 placeholder:text-slate-400"
                                    disabled={isLoading}
                                />
                                {/* Voice Input Button */}
                                <button
                                    type="button"
                                    onClick={toggleVoiceInput}
                                    disabled={isLoading || isTranscribing}
                                    className={`absolute right-3 top-1/2 -translate-y-1/2 transition-all duration-200 ${
                                        isTranscribing
                                            ? 'text-blue-500'
                                            : isListening
                                            ? 'text-red-500 hover:text-red-600'
                                            : 'text-slate-400 hover:text-slate-600'
                                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                                    title={isTranscribing ? 'Transcribing...' : isListening ? 'Stop listening' : 'Voice input'}
                                >
                                    {/* Pulse ring when listening */}
                                    {isListening && (
                                        <span className="absolute inset-0 -m-1.5 rounded-full border-2 border-red-400 animate-ping opacity-50" />
                                    )}
                                    {isTranscribing ? (
                                        <Loader2 size={16} className="animate-spin text-blue-500" />
                                    ) : isListening ? (
                                        <MicOff size={16} />
                                    ) : (
                                        <Mic size={16} />
                                    )}
                                </button>
                            </div>

                            <button
                                type="submit"
                                disabled={!input.trim() || isLoading}
                                className={`flex-shrink-0 w-11 h-11 rounded-full flex items-center justify-center transition-all duration-200 ${input.trim() && !isLoading
                                    ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20 hover:bg-blue-700 hover:shadow-lg hover:shadow-blue-600/25 hover:-translate-y-0.5 active:scale-90'
                                    : 'bg-blue-50 text-blue-300 cursor-not-allowed'
                                    }`}
                            >
                                {isLoading ? (
                                    <Loader2 className="animate-spin" size={18} />
                                ) : (
                                    <Send size={18} className={input.trim() ? 'translate-x-[1px]' : ''} />
                                )}
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ChatInterface;
