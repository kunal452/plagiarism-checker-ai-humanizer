import React, { useState } from 'react';
import {
  Wand2,
  Sparkles,
  Download,
  Copy,
  Check,
  ShieldCheck,
  Zap,
  Sliders,
  FileCheck,
  ArrowRight,
  RefreshCw,
  GitCompare,
  Eye,
  AlertCircle
} from 'lucide-react';
import DiffViewer from './DiffViewer';

export default function HumanizerStudio({ text, setText, onSendToPlagiarism }) {
  const [humanizedText, setHumanizedText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [viewMode, setViewMode] = useState('clean'); // 'clean' or 'diff'
  const [mode, setMode] = useState('academic');
  const [burstinessLevel, setBurstinessLevel] = useState('balanced');
  const [backend, setBackend] = useState('auto');
  const [modelName, setModelName] = useState('llama3:8b');
  const [temperature, setTemperature] = useState(0.70);
  const [preserveCitations, setPreserveCitations] = useState(true);
  const [resultMeta, setResultMeta] = useState(null);
  const [copied, setCopied] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const runHumanizer = async () => {
    if (!text.trim()) {
      setErrorMsg('Please enter or paste text to humanize.');
      return;
    }
    setErrorMsg('');
    setIsProcessing(true);

    try {
      const res = await fetch('/api/humanize/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text,
          mode,
          backend,
          model_name: modelName,
          temperature,
          burstiness_level: burstinessLevel,
          preserve_citations: preserveCitations
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Humanization failed.');
      }

      const data = await res.json();
      setHumanizedText(data.humanized_text);
      setResultMeta(data);
    } catch (err) {
      setErrorMsg(err.message || 'Error executing humanizer.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCopy = () => {
    if (!humanizedText) return;
    navigator.clipboard.writeText(humanizedText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = async (format) => {
    if (!humanizedText) return;
    try {
      const res = await fetch(`/api/export/${format}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: humanizedText,
          title: 'Humanized Document'
        }),
      });
      if (!res.ok) throw new Error('Download failed');

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `humanized_document.${format}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setErrorMsg(`Failed to export ${format.toUpperCase()}`);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Control Configuration Bar */}
      <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-6 shadow-xl">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-purple-600/20 border border-purple-500/30 flex items-center justify-center text-purple-400">
              <Sliders className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-white">AI Humanizer Configuration</h2>
              <p className="text-xs text-slate-400">Perplexity modulation, burstiness injection, and cliché eradication</p>
            </div>
          </div>

          {/* Quick Selectors */}
          <div className="flex flex-wrap items-center gap-4 text-xs">
            {/* Tone Mode */}
            <div>
              <label className="block text-slate-400 mb-1 font-medium">Style Mode</label>
              <select
                value={mode}
                onChange={(e) => setMode(e.target.value)}
                className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-purple-500"
              >
                <option value="academic">Academic & Rigorous</option>
                <option value="conversational">Conversational & Natural</option>
                <option value="professional">Executive & Direct</option>
                <option value="creative">Creative & Rhythmic</option>
              </select>
            </div>

            {/* Burstiness Level */}
            <div>
              <label className="block text-slate-400 mb-1 font-medium">Burstiness Variance</label>
              <select
                value={burstinessLevel}
                onChange={(e) => setBurstinessLevel(e.target.value)}
                className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-purple-500"
              >
                <option value="balanced">Balanced (High Naturality)</option>
                <option value="aggressive">Aggressive (Maximum Variance)</option>
                <option value="subtle">Subtle (Light Touch)</option>
              </select>
            </div>

            {/* LLM Inference Engine */}
            <div>
              <label className="block text-slate-400 mb-1 font-medium">Inference Backend</label>
              <select
                value={backend}
                onChange={(e) => setBackend(e.target.value)}
                className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-purple-500"
              >
                <option value="auto">Auto / Smart Burstiness Engine</option>
                <option value="ollama">Local Ollama (Llama-3 / Mistral)</option>
                <option value="vllm">Self-hosted vLLM (:8000/v1)</option>
              </select>
            </div>

            {/* Fact Preservation Toggle */}
            <div className="pt-4">
              <label className="flex items-center gap-2 cursor-pointer text-slate-300">
                <input
                  type="checkbox"
                  checked={preserveCitations}
                  onChange={(e) => setPreserveCitations(e.target.checked)}
                  className="rounded border-slate-700 text-purple-600 focus:ring-0 bg-slate-800"
                />
                <span className="font-medium text-xs">Fact & Citation Guard</span>
              </label>
            </div>

            {/* Run Button */}
            <div className="pt-4">
              <button
                onClick={runHumanizer}
                disabled={isProcessing || !text.trim()}
                className="flex items-center gap-2 px-5 py-2 rounded-xl font-medium text-sm text-white bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 shadow-lg shadow-purple-600/30 transition disabled:opacity-50"
              >
                {isProcessing ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Humanizing Chunks...</span>
                  </>
                ) : (
                  <>
                    <Wand2 className="w-4 h-4" />
                    <span>Humanize Text</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {errorMsg && (
          <div className="mt-4 text-xs bg-rose-950/60 border border-rose-800 text-rose-300 p-3 rounded-lg flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}
      </div>

      {/* Split-Screen Studio */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Pane: Original AI Draft */}
        <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-6 flex flex-col justify-between shadow-xl">
          <div>
            <div className="flex justify-between items-center mb-3">
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold text-white">Original Document / AI Draft</h3>
                {resultMeta?.original_metrics && (
                  <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${
                    resultMeta.original_metrics.ai_probability > 60
                      ? 'bg-rose-950 text-rose-300 border border-rose-800'
                      : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                  }`}>
                    {resultMeta.original_metrics.ai_probability}% AI Probability
                  </span>
                )}
              </div>
              <span className="text-xs text-slate-500 font-mono">
                {text ? `${text.split(/\s+/).filter(Boolean).length} words` : '0 words'}
              </span>
            </div>

            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={16}
              placeholder="Paste formulaic AI text or draft to humanize..."
              className="w-full bg-slate-950/80 border border-slate-800 rounded-xl p-4 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-purple-500 font-sans leading-relaxed resize-none"
            />
          </div>

          {/* AI Detector Breakdown for Original */}
          {resultMeta?.original_metrics && (
            <div className="mt-4 p-3 bg-slate-950 rounded-xl border border-slate-800/80 grid grid-cols-3 gap-2 text-center text-xs">
              <div>
                <span className="text-slate-500 block text-[10px]">Burstiness</span>
                <span className="font-semibold text-rose-400">{resultMeta.original_metrics.burstiness} (Low)</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px]">Perplexity</span>
                <span className="font-semibold text-rose-400">{resultMeta.original_metrics.perplexity_estimate}</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px]">AI Clichés Found</span>
                <span className="font-semibold text-rose-400">{resultMeta.original_metrics.total_markers} markers</span>
              </div>
            </div>
          )}
        </div>

        {/* Right Pane: Humanized Output */}
        <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-6 flex flex-col justify-between shadow-xl">
          <div>
            <div className="flex justify-between items-center mb-3">
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold text-white">Humanized Natural Text</h3>
                {resultMeta?.humanized_metrics && (
                  <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800">
                    {resultMeta.humanized_metrics.ai_probability}% AI ({resultMeta.humanized_metrics.classification})
                  </span>
                )}
              </div>

              {/* View Mode Toggle: Clean vs Diff */}
              {humanizedText && (
                <div className="flex items-center bg-slate-950 p-0.5 rounded-lg border border-slate-800 text-xs">
                  <button
                    onClick={() => setViewMode('clean')}
                    className={`flex items-center gap-1 px-2.5 py-1 rounded transition ${
                      viewMode === 'clean' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    <Eye className="w-3.5 h-3.5" />
                    <span>Clean</span>
                  </button>
                  <button
                    onClick={() => setViewMode('diff')}
                    className={`flex items-center gap-1 px-2.5 py-1 rounded transition ${
                      viewMode === 'diff' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    <GitCompare className="w-3.5 h-3.5" />
                    <span>Diff View</span>
                  </button>
                </div>
              )}
            </div>

            {/* Display Body */}
            {viewMode === 'diff' && humanizedText ? (
              <DiffViewer originalText={text} modifiedText={humanizedText} />
            ) : (
              <textarea
                readOnly
                value={humanizedText}
                rows={16}
                placeholder="Humanized text with varied burstiness and authentic phrasing will appear here..."
                className="w-full bg-slate-950/80 border border-slate-800 rounded-xl p-4 text-sm text-slate-200 placeholder-slate-600 focus:outline-none font-sans leading-relaxed resize-none"
              />
            )}
          </div>

          {/* Post-Humanization Metrics & Actions */}
          <div className="mt-4 space-y-3">
            {resultMeta?.humanized_metrics && (
              <div className="p-3 bg-slate-950 rounded-xl border border-slate-800/80 grid grid-cols-3 gap-2 text-center text-xs">
                <div>
                  <span className="text-slate-500 block text-[10px]">Burstiness Boost</span>
                  <span className="font-semibold text-emerald-400">{resultMeta.humanized_metrics.burstiness} (Varied)</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px]">Perplexity Boost</span>
                  <span className="font-semibold text-emerald-400">{resultMeta.humanized_metrics.perplexity_estimate}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px]">Fact Fidelity</span>
                  <span className="font-semibold text-emerald-400">
                    {resultMeta.fidelity?.fidelity_score || 100}% Preserved
                  </span>
                </div>
              </div>
            )}

            {/* Action Bar */}
            {humanizedText && (
              <div className="flex flex-wrap items-center justify-between gap-2 pt-2">
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleCopy}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium border border-slate-700 transition"
                  >
                    {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copied ? 'Copied' : 'Copy'}</span>
                  </button>

                  <button
                    onClick={() => handleDownload('docx')}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium border border-slate-700 transition"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>DOCX</span>
                  </button>

                  <button
                    onClick={() => handleDownload('pdf')}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium border border-slate-700 transition"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>PDF</span>
                  </button>
                </div>

                {/* Send directly to Plagiarism Checker to verify 0% Plagiarism */}
                <button
                  onClick={() => onSendToPlagiarism(humanizedText)}
                  className="flex items-center gap-1.5 px-3.5 py-1.5 bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-300 border border-indigo-500/40 rounded-lg text-xs font-medium transition"
                >
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>Verify in Plagiarism Checker</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
