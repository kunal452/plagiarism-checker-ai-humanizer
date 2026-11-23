import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import PlagiarismChecker from './components/PlagiarismChecker';
import HumanizerStudio from './components/HumanizerStudio';
import CorpusManager from './components/CorpusManager';
import { SAMPLE_TEXTS } from './data/sampleTexts';
import { ShieldCheck, Wand2, Layers, Cpu, Database } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('plagiarism');
  const [documentText, setDocumentText] = useState(SAMPLE_TEXTS.plagiarism_mix);
  const [isBackendOnline, setIsBackendOnline] = useState(false);

  // Check backend health
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch('/api/health');
        if (res.ok) {
          setIsBackendOnline(true);
        } else {
          setIsBackendOnline(false);
        }
      } catch {
        setIsBackendOnline(false);
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 8000);
    return () => clearInterval(interval);
  }, []);

  const handleSelectSample = (sampleKey) => {
    const chosen = SAMPLE_TEXTS[sampleKey];
    if (chosen) {
      setDocumentText(chosen);
      if (sampleKey === 'ai_robotic') {
        setActiveTab('humanizer');
      } else {
        setActiveTab('plagiarism');
      }
    }
  };

  const handleSendToHumanizer = (textToHumanize) => {
    setDocumentText(textToHumanize);
    setActiveTab('humanizer');
  };

  const handleSendToPlagiarism = (humanizedText) => {
    setDocumentText(humanizedText);
    setActiveTab('plagiarism');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-indigo-500/30 selection:text-indigo-200">
      {/* Top Navigation */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onSelectSample={handleSelectSample}
        isBackendOnline={isBackendOnline}
      />

      {/* Main Interactive Stage */}
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
        {activeTab === 'plagiarism' && (
          <PlagiarismChecker
            text={documentText}
            setText={setDocumentText}
            onSendToHumanizer={handleSendToHumanizer}
          />
        )}

        {activeTab === 'humanizer' && (
          <HumanizerStudio
            text={documentText}
            setText={setDocumentText}
            onSendToPlagiarism={handleSendToPlagiarism}
          />
        )}

        {activeTab === 'corpus' && (
          <CorpusManager />
        )}
      </main>

      {/* System Architecture Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/90 py-6 px-6 mt-12 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-400">Veritas Dual-Pipeline Engine</span>
            <span>•</span>
            <span>Turnitin-Style MinHash (LSH) & Rabin-Karp Exact Shingles + Dense Vector Cosine Similarity</span>
          </div>

          <div className="flex items-center gap-4 text-[11px] text-slate-400">
            <span className="flex items-center gap-1">
              <Cpu className="w-3.5 h-3.5 text-indigo-400" /> PyMuPDF & docx Parser
            </span>
            <span className="flex items-center gap-1">
              <Database className="w-3.5 h-3.5 text-purple-400" /> Vector Corpus Index
            </span>
            <span className="flex items-center gap-1">
              <Layers className="w-3.5 h-3.5 text-pink-400" /> vLLM / Ollama Chunked Rewriter
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
