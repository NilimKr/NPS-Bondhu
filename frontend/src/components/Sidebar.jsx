import React, { useState } from 'react';
import { Globe, Info, ShieldCheck, X, MessageSquarePlus, Sparkles, ChevronDown } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const Sidebar = ({ language, setLanguage, isOpen, onClose }) => {
    const [isLangOpen, setIsLangOpen] = useState(false);

    const languages = [
        { code: 'en', label: 'English', native: 'English' },
        { code: 'hi', label: 'Hindi', native: 'हिन्दी' },
        { code: 'as', label: 'Assamese', native: 'অসমীয়া' },
    ];

    const content = {
        en: {
            about: 'About NPS Bondhu',
            description:
                'Your AI-powered assistant for the National Pension System. Retrieves information directly from official PFRDA regulations.',
            secured: 'Official Data Sources',
            newChat: 'New Chat',
        },
        hi: {
            about: 'NPS Bondhu के बारे में',
            description:
                'राष्ट्रीय पेंशन प्रणाली के लिए आपका AI-पावर्ड सहायक। आधिकारिक PFRDA नियमों से सीधे जानकारी प्राप्त करता है।',
            secured: 'आधिकारिक डेटा स्रोत',
            newChat: 'नई चैट',
        },
        as: {
            about: 'NPS Bondhu ৰ বিষয়ে',
            description:
                'ৰাষ্ট্ৰীয় পেঞ্চন ব্যৱস্থাৰ বাবে আপোনাৰ AI-চালিত সহায়ক। চৰকাৰী PFRDA নিয়মৰ পৰা তথ্য সংগ্ৰহ কৰে।',
            secured: 'চৰকাৰী তথ্যৰ উৎস',
            newChat: 'নতুন চেট',
        },
    };

    const t = content[language] || content['en'];
    const currentLang = languages.find(l => l.code === language) || languages[0];

    return (
        <aside
            className={`
        fixed top-0 left-0 z-50 h-screen w-72 flex flex-col
        bg-gradient-to-b from-blue-50/80 via-slate-50 to-indigo-50/60
        text-slate-700 border-r border-blue-100/60
        sidebar-drawer
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        md:translate-x-0
      `}
        >
            {/* Close button (mobile) */}
            <button
                onClick={onClose}
                className="md:hidden absolute top-4 right-4 p-1.5 rounded-lg text-slate-400
          hover:text-slate-600 hover:bg-blue-100/50 hover:rotate-90
          transition-all duration-200"
                aria-label="Close sidebar"
            >
                <X size={18} />
            </button>

            {/* Branding */}
            <div className="px-5 pt-7 pb-5 text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl
          bg-gradient-to-br from-blue-500 via-indigo-500 to-blue-600
          shadow-lg shadow-blue-400/20 mb-3
          hover:shadow-xl hover:shadow-blue-400/30 hover:scale-105
          transition-all duration-300">
                    <Sparkles size={22} className="text-white" />
                </div>
                <h1 className="text-lg font-bold tracking-tight text-slate-800">NPS Bondhu</h1>
                <p className="text-[11px] text-blue-400/70 tracking-[0.12em] uppercase mt-0.5 font-medium">
                    Official Assistant
                </p>
            </div>

            {/* New Chat Button */}
            <div className="px-4 mb-1">
                <button
                    onClick={() => window.location.reload()}
                    className="w-full flex items-center gap-2.5 px-4 py-2.5 rounded-xl
            bg-white/70 border border-blue-100/60
            text-sm font-medium text-slate-600
            hover:bg-blue-50/80 hover:border-blue-200 hover:text-blue-700
            hover:shadow-md hover:shadow-blue-100/40 hover:-translate-y-0.5
            active:scale-[0.98]
            transition-all duration-200"
                >
                    <MessageSquarePlus size={16} />
                    {t.newChat}
                </button>
            </div>

            {/* Divider */}
            <div className="mx-5 my-3 border-t border-blue-100/40" />

            {/* Language Selector Dropdown */}
            <div className="px-4 flex-1">
                <label className="flex items-center gap-2 text-[11px] font-semibold text-slate-400/80 uppercase tracking-wider mb-2.5 px-1">
                    <Globe size={13} />
                    Language
                </label>

                <div className="relative">
                    <button
                        onClick={() => setIsLangOpen(!isLangOpen)}
                        className="w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl
                            bg-white/50 border border-blue-100/60 text-slate-600
                            hover:bg-white/80 hover:border-blue-200 hover:shadow-sm hover:shadow-blue-100/30
                            transition-all duration-200"
                    >
                        <div className="flex flex-col items-start text-left">
                            <span className="text-sm font-medium leading-tight">{currentLang.native}</span>
                            {currentLang.native !== currentLang.label && (
                                <span className="text-[10px] text-slate-400">{currentLang.label}</span>
                            )}
                        </div>
                        <ChevronDown
                            size={16}
                            className={`text-slate-400 transition-transform duration-200 ${isLangOpen ? 'rotate-180' : ''}`}
                        />
                    </button>

                    <AnimatePresence>
                        {isLangOpen && (
                            <motion.div
                                initial={{ opacity: 0, y: -10, scale: 0.95 }}
                                animate={{ opacity: 1, y: 0, scale: 1 }}
                                exit={{ opacity: 0, y: -10, scale: 0.95 }}
                                transition={{ duration: 0.15 }}
                                className="absolute top-full left-0 w-full mt-2 p-1.5 z-10
                                    bg-white/90 backdrop-blur-md border border-blue-100/60 rounded-xl
                                    shadow-lg shadow-blue-500/10"
                            >
                                {languages.map((lang) => (
                                    <button
                                        key={lang.code}
                                        onClick={() => {
                                            setLanguage(lang.code);
                                            setIsLangOpen(false);
                                            onClose();
                                        }}
                                        className={`w-full text-left flex items-center justify-between px-3 py-2 rounded-lg mb-0.5
                                            transition-all duration-150
                                            ${language === lang.code
                                                ? 'bg-blue-50 text-blue-600'
                                                : 'text-slate-600 hover:bg-slate-50'
                                            }`}
                                    >
                                        <div className="flex flex-col">
                                            <span className="text-sm font-medium leading-tight">{lang.native}</span>
                                            {lang.native !== lang.label && (
                                                <span className="text-[10px] text-slate-400">{lang.label}</span>
                                            )}
                                        </div>
                                        {language === lang.code && (
                                            <div className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                                        )}
                                    </button>
                                ))}
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>

            {/* About Section */}
            <div className="px-4 pb-5 mt-auto">
                <div className="p-3.5 rounded-xl bg-white/60 border border-blue-100/40 backdrop-blur-sm
          hover:bg-white/80 hover:shadow-sm transition-all duration-200">
                    <div className="flex items-center gap-2 text-blue-500 mb-1.5">
                        <Info size={14} />
                        <h3 className="font-semibold text-xs">{t.about}</h3>
                    </div>
                    <p className="text-[11px] text-slate-500 leading-relaxed">{t.description}</p>

                    <div className="mt-3 flex items-center gap-2 text-emerald-600 text-[11px] font-medium
            bg-emerald-50/80 px-2.5 py-1.5 rounded-lg border border-emerald-100/60">
                        <ShieldCheck size={13} />
                        {t.secured}
                    </div>
                </div>

                <p className="text-center text-[10px] text-slate-400/70 mt-3">
                    Powered by Official NPS Documents
                </p>
            </div>
        </aside>
    );
};

export default Sidebar;
