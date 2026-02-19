import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { User, Bot, Copy, Check, FileText, ChevronDown, ChevronUp } from 'lucide-react';
import { motion } from 'framer-motion';

const MessageBubble = ({ message }) => {
    const isUser = message.role === 'user';
    const [copied, setCopied] = useState(false);
    const [sourcesExpanded, setSourcesExpanded] = useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText(message.content);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const formatTime = (date) => {
        if (!date) return '';
        const d = new Date(date);
        return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    return (
        <div className={`flex w-full mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
            <div
                className={`flex gap-2.5 ${isUser ? 'flex-row-reverse max-w-[80%]' : 'flex-row max-w-[85%]'}`}
            >
                {/* Avatar */}
                <div
                    className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center mt-1 ${isUser
                        ? 'bg-blue-600 text-white'
                        : 'bg-emerald-500 text-white shadow-sm'
                        }`}
                >
                    {isUser ? <User size={14} strokeWidth={2.5} /> : <Bot size={14} strokeWidth={2.5} />}
                </div>

                {/* Bubble + timestamp */}
                <div className="group flex flex-col">
                    <div
                        className={`relative px-4 py-3 text-[13.5px] leading-relaxed ${isUser
                            ? 'bg-blue-600 text-white rounded-2xl rounded-tr-md shadow-sm'
                            : 'bg-white text-slate-700 border border-slate-200/80 rounded-2xl rounded-tl-md shadow-sm'
                            }`}
                    >
                        {/* Message Content */}
                        <div className={isUser ? '' : 'markdown-body'}>
                            {isUser ? (
                                <p className="whitespace-pre-wrap">{message.content}</p>
                            ) : (
                                <ReactMarkdown
                                    components={{
                                        a: ({ node, ...props }) => (
                                            <a
                                                {...props}
                                                className="text-blue-600 hover:text-blue-700 underline decoration-blue-200 underline-offset-2"
                                                target="_blank"
                                                rel="noopener noreferrer"
                                            />
                                        ),
                                        strong: ({ node, ...props }) => (
                                            <span {...props} className="font-semibold text-slate-800" />
                                        ),
                                        ul: ({ node, ...props }) => (
                                            <ul {...props} className="list-disc list-outside ml-4 my-1.5 space-y-0.5" />
                                        ),
                                        ol: ({ node, ...props }) => (
                                            <ol
                                                {...props}
                                                className="list-decimal list-outside ml-4 my-1.5 space-y-0.5"
                                            />
                                        ),
                                        li: ({ node, ...props }) => <li {...props} className="leading-relaxed" />,
                                        p: ({ node, ...props }) => <p {...props} className="mb-2 last:mb-0" />,
                                    }}
                                >
                                    {message.content}
                                </ReactMarkdown>
                            )}
                        </div>

                        {/* Source Attribution — expandable like reference image */}
                        {!isUser && message.sources && (
                            <div className="mt-3 pt-2.5 border-t border-slate-100">
                                <button
                                    onClick={() => setSourcesExpanded(!sourcesExpanded)}
                                    className="flex items-center gap-1.5 w-full text-left group/src
                                      hover:text-blue-500 transition-colors duration-200 py-0.5 rounded-md"
                                >
                                    <FileText size={12} className="text-slate-400 group-hover/src:text-blue-400 transition-colors" />
                                    <span className="text-[11px] font-semibold text-slate-400 group-hover/src:text-blue-500 uppercase tracking-wider flex-1 transition-colors">
                                        Source Attribution
                                    </span>
                                    {sourcesExpanded ? (
                                        <ChevronUp size={14} className="text-slate-400 group-hover/src:text-blue-400 transition-colors" />
                                    ) : (
                                        <ChevronDown size={14} className="text-slate-400 group-hover/src:text-blue-400 transition-colors" />
                                    )}
                                </button>
                                {sourcesExpanded && (
                                    <motion.div
                                        initial={{ opacity: 0, height: 0 }}
                                        animate={{ opacity: 1, height: 'auto' }}
                                        transition={{ duration: 0.2 }}
                                        className="mt-2"
                                    >
                                        <div className="text-[12px] text-slate-500 bg-slate-50/80 px-3 py-2.5 rounded-lg border border-slate-100 whitespace-pre-wrap leading-relaxed">
                                            {message.sources}
                                        </div>
                                    </motion.div>
                                )}
                            </div>
                        )}
                    </div>

                    {/* Timestamp + Copy */}
                    <div className={`flex items-center gap-2 mt-1 px-1 ${isUser ? 'justify-end' : 'justify-start'}`}>
                        {message.timestamp && (
                            <span className="text-[10px] text-slate-400">{formatTime(message.timestamp)}</span>
                        )}
                        {!isUser && (
                            <button
                                onClick={handleCopy}
                                className="flex items-center gap-1 px-1.5 py-0.5 rounded
                  text-[10px] text-slate-400 hover:text-blue-600
                  opacity-0 group-hover:opacity-100 transition-all duration-200"
                                title="Copy response"
                            >
                                {copied ? (
                                    <>
                                        <Check size={11} /> Copied
                                    </>
                                ) : (
                                    <>
                                        <Copy size={11} /> Copy
                                    </>
                                )}
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MessageBubble;
