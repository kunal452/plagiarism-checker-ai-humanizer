import React from 'react';
import { ShieldCheck, Wand2, BookOpen, Sparkles, CheckCircle2 } from 'lucide-react';

export default function Header({ activeTab, setActiveTab, onSelectSample, isBackendOnline }) {
  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50 px-6 py-3.5">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center shadow-lg shadow-indigo-500/25">
            <ShieldCheck className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent">
                Veritas AI
              </span>
              <span className="text-[10px] font-semibold tracking-wider uppercase px-2 py-0.5 rounded-full bg-indigo-950 text-indigo-400 border border-indigo-800/60">
                Turnitin & Humanizer Suite
              </span>
            </div>
            <p className="text-xs text-slate-400">Dual-Layer Plagiarism Matcher & Unlimited AI Text Humanizer</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center bg-slate-950/70 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab('plagiarism')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'plagiarism'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <ShieldCheck className="w-4 h-4" />
            <span>Plagiarism Inspector</span>
          </button>

          <button
            onClick={() => setActiveTab('humanizer')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'humanizer'
                ? 'bg-purple-600 text-white shadow-md shadow-purple-600/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Wand2 className="w-4 h-4" />
            <span>AI Humanizer Studio</span>
          </button>

          <button
            onClick={() => setActiveTab('corpus')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'corpus'
                ? 'bg-slate-800 text-white'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <BookOpen className="w-4 h-4" />
            <span>Reference Corpus</span>
          </button>
        </div>

        {/* Quick Samples & Backend Status */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full bg-slate-950 border border-slate-800">
            <span className={`w-2 h-2 rounded-full ${isBackendOnline ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
            <span className="text-slate-400">{isBackendOnline ? 'API Connected' : 'Connecting...'}</span>
          </div>

          <div className="flex items-center gap-1 text-xs">
            <span className="text-slate-500 mr-1 hidden sm:inline">Samples:</span>
            <button
              onClick={() => onSelectSample('plagiarism_mix')}
              className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 transition"
              title="Load document containing copied & paraphrased content from corpus"
            >
              Plagiarism Mix
            </button>
            <button
              onClick={() => onSelectSample('ai_robotic')}
              className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 transition"
              title="Load formulaic AI text with low burstiness"
            >
              AI Cliché Text
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
