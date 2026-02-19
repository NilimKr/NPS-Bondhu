import React from 'react';
import { Menu } from 'lucide-react';

const MobileHeader = ({ onMenuClick }) => {
    return (
        <div className="md:hidden sticky top-0 z-30 bg-white/90 backdrop-blur-lg border-b border-slate-100">
            <div className="flex items-center justify-between px-4 py-3">
                <button
                    onClick={onMenuClick}
                    className="p-2 -ml-2 rounded-xl hover:bg-slate-100 transition-colors text-slate-500"
                    aria-label="Open sidebar"
                >
                    <Menu size={20} />
                </button>

                <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
                        <span className="text-white text-xs font-bold">N</span>
                    </div>
                    <div>
                        <h1 className="font-bold text-sm text-slate-800 leading-tight">NPS Bondhu</h1>
                        <p className="text-[10px] text-emerald-500 font-medium leading-tight flex items-center gap-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block" />
                            Official Assistant
                        </p>
                    </div>
                </div>

                {/* Spacer */}
                <div className="w-10" />
            </div>
        </div>
    );
};

export default MobileHeader;
