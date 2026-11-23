import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, Check, AlertTriangle, ShieldAlert, Sparkles, Filter, ExternalLink, RefreshCw, X, ArrowRight } from 'lucide-react';

export default function PlagiarismChecker({ text, setText, onSendToHumanizer }) {
  const [file, setFile] = useState(null);
  const [excludeQuotes, setExcludeQuotes] = useState(true);
  const [excludeBibliography, setExcludeBibliography] = useState(true);
  const [minShingleSize, setMinShingleSize] = useState(5);
  const [isScanning, setIsScanning] = useState(false);
  const [scanResult, setScanResult] = useState(null);
  const [selectedSpan, setSelectedSpan] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  const fileInputRef = useRef(null);

  const handleFileUpload = async (e) => {
    const uploadedFile = e.target.files?.[0];
    if (!uploadedFile) return;
    setFile(uploadedFile);
    setErrorMsg('');

    // Pre-parse document
    const formData = new FormData();
    formData.append('file', uploadedFile);
    try {
      const res = await fetch('/api/documents/parse', {
        method: 'POST',
        body: formData,
      });
      if (res.ok) {
        const data = await res.json();
        setText(data.text || '');
      } else {
        setErrorMsg('Could not parse document file.');
      }
    } catch (err) {
      setErrorMsg('Failed to connect to parser service.');
    }
  };

  const runPlagiarismScan = async () => {
    if (!text.trim() && !file) {
      setErrorMsg('Please upload a document or paste text to analyze.');
      return;
    }
    setErrorMsg('');
    setIsScanning(true);
    setScanResult(null);
    setSelectedSpan(null);

    try {
      const formData = new FormData();
      if (file) {
        formData.append('file', file);
      } else {
        formData.append('text', text);
      }
      formData.append('exclude_quotes', excludeQuotes.toString());
      formData.append('exclude_bibliography', excludeBibliography.toString());
      formData.append('min_shingle_size', minShingleSize.toString());

      const res = await fetch('/api/plagiarism/check', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Plagiarism scan failed.');
      }

      const data = await res.json();
      setScanResult(data);
    } catch (err) {
      setErrorMsg(err.message || 'Error executing plagiarism scan.');
    } finally {
      setIsScanning(false);
    }
  };

  // Render text with interactive highlighted spans
  const renderHighlightedDocument = () => {
    if (!scanResult || !scanResult.raw_text) {
      return (
        <div className="p-4 text-slate-400 italic">No document loaded.</div>
      );
    }

    const raw = scanResult.raw_text;
    const spans = scanResult.matched_spans || [];

    if (spans.length === 0) {
      return (
        <div className="p-6 bg-slate-950/60 rounded-xl border border-slate-800 text-slate-300 leading-relaxed font-sans whitespace-pre-wrap">
          {raw}
        </div>
      );
    }

    // Sort spans by start offset
    const sorted = [...spans].sort((a, b) => a.start - b.start);
    const elements = [];
    let lastIdx = 0;

    sorted.forEach((span, idx) => {
      // Unmatched leading text
      if (span.start > lastIdx) {
        elements.push(
          <span key={`unmatched-${lastIdx}`} className="text-slate-300">
            {raw.substring(lastIdx, span.start)}
          </span>
        );
      }

      const isExact = span.match_type === 'exact';
      const isSelected = selectedSpan && selectedSpan.start === span.start;

      // Matched highlighted span
      elements.push(
        <mark
          key={`span-${idx}`}
          onClick={() => setSelectedSpan(span)}
          className={`cursor-pointer transition-all px-1 py-0.5 rounded ${
            isExact
              ? 'bg-rose-500/25 hover:bg-rose-500/40 text-rose-200 border-b-2 border-rose-500 font-medium'
              : 'bg-amber-500/25 hover:bg-amber-500/40 text-amber-200 border-b-2 border-amber-500 font-medium'
          } ${isSelected ? 'ring-2 ring-white shadow-lg' : ''}`}
          title={`${isExact ? 'Exact Match' : 'Paraphrase'} from: ${span.source_title}`}
        >
          {raw.substring(span.start, span.end)}
          <sup className={`ml-1 text-[10px] font-bold px-1 rounded ${isExact ? 'bg-rose-900 text-rose-200' : 'bg-amber-900 text-amber-200'}`}>
            {span.source_id.startsWith('ref-') ? span.source_id.replace('ref-', '#') : '#'}
          </sup>
        </mark>
      );

      lastIdx = span.end;
    });

    if (lastIdx < raw.length) {
      elements.push(
        <span key={`tail-${lastIdx}`} className="text-slate-300">
          {raw.substring(lastIdx)}
        </span>
      );
    }

    return (
      <div className="p-6 bg-slate-950/70 rounded-xl border border-slate-800 text-slate-200 leading-relaxed font-sans whitespace-pre-wrap max-h-[600px] overflow-y-auto">
        {elements}
      </div>
    );
  };

  const getScoreColor = (pct) => {
    if (pct < 15) return 'text-emerald-400 border-emerald-500/40 bg-emerald-950/30';
    if (pct < 30) return 'text-amber-400 border-amber-500/40 bg-amber-950/30';
    if (pct < 50) return 'text-orange-400 border-orange-500/40 bg-orange-950/30';
    return 'text-rose-500 border-rose-500/40 bg-rose-950/30';
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Input Section */}
      <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-6 shadow-xl">
        <div className="flex flex-col md:flex-row gap-6">
          {/* File Dropzone */}
          <div className="md:w-1/3 flex flex-col justify-between">
            <div>
              <h2 className="text-base font-semibold text-white mb-2 flex items-center gap-2">
                <FileText className="w-5 h-5 text-indigo-400" />
                Upload Document
              </h2>
              <p className="text-xs text-slate-400 mb-4">
                Accepts PDF, Word (.docx), or plain text. Preserves paragraphs and formatting coordinates.
              </p>

              <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-slate-700 hover:border-indigo-500/80 rounded-xl p-6 text-center cursor-pointer transition bg-slate-950/50 hover:bg-slate-950/80 group"
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.docx,.doc,.txt"
                  className="hidden"
                  onChange={handleFileUpload}
                />
                <UploadCloud className="w-10 h-10 text-slate-500 group-hover:text-indigo-400 mx-auto mb-2 transition" />
                <p className="text-sm font-medium text-slate-300">
                  {file ? file.name : 'Click or drop PDF / DOCX here'}
                </p>
                <p className="text-xs text-slate-500 mt-1">PyMuPDF & python-docx engine</p>
              </div>

              {file && (
                <div className="mt-3 flex items-center justify-between text-xs bg-slate-800/80 px-3 py-2 rounded-lg border border-slate-700">
                  <span className="truncate text-slate-300">{file.name}</span>
                  <button
                    onClick={() => { setFile(null); }}
                    className="text-slate-400 hover:text-white"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>

            {/* Smart Exclusion Filters */}
            <div className="mt-6 pt-4 border-t border-slate-800/80 space-y-3">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <Filter className="w-3.5 h-3.5" /> False-Positive Filters
              </span>

              <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={excludeQuotes}
                  onChange={(e) => setExcludeQuotes(e.target.checked)}
                  className="rounded border-slate-700 text-indigo-600 focus:ring-0 bg-slate-800"
                />
                <span>Exclude Quotations (<span className="text-slate-400">“...” text in quotes</span>)</span>
              </label>

              <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={excludeBibliography}
                  onChange={(e) => setExcludeBibliography(e.target.checked)}
                  className="rounded border-slate-700 text-indigo-600 focus:ring-0 bg-slate-800"
                />
                <span>Exclude Bibliography (<span className="text-slate-400">Works Cited / References</span>)</span>
              </label>

              <div className="pt-2">
                <div className="flex justify-between text-xs text-slate-400 mb-1">
                  <span>Match Sensitivity (Min Shingle)</span>
                  <span className="font-semibold text-indigo-400">{minShingleSize} words</span>
                </div>
                <input
                  type="range"
                  min="4"
                  max="8"
                  value={minShingleSize}
                  onChange={(e) => setMinShingleSize(parseInt(e.target.value))}
                  className="w-full accent-indigo-500 h-1.5 bg-slate-800 rounded-lg cursor-pointer"
                />
              </div>
            </div>
          </div>

          {/* Text Area & Submit */}
          <div className="md:w-2/3 flex flex-col justify-between">
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm font-semibold text-white">Document Text</label>
                <span className="text-xs text-slate-400 font-mono">
                  {text ? `${text.split(/\s+/).filter(Boolean).length} words` : '0 words'}
                </span>
              </div>
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                rows={12}
                placeholder="Paste academic essay, research draft, or article text here..."
                className="w-full bg-slate-950/80 border border-slate-800 rounded-xl p-4 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500 font-sans leading-relaxed resize-none"
              />
            </div>

            {errorMsg && (
              <div className="mt-3 text-xs bg-rose-950/60 border border-rose-800/80 text-rose-300 p-3 rounded-lg flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            <div className="mt-4 flex justify-end gap-3">
              <button
                onClick={runPlagiarismScan}
                disabled={isScanning || (!text.trim() && !file)}
                className="flex items-center gap-2 px-6 py-2.5 rounded-xl font-medium text-sm text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 shadow-lg shadow-indigo-600/30 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isScanning ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Scanning Dual-Layer Corpus...</span>
                  </>
                ) : (
                  <>
                    <ShieldAlert className="w-4 h-4" />
                    <span>Run Plagiarism Scan</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Turnitin-Style Report Section */}
      {scanResult && (
        <div className="space-y-6 animate-fadeIn">
          {/* Top Score Banner */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Overall Similarity Circular Card */}
            <div className={`p-5 rounded-2xl border ${getScoreColor(scanResult.overall_similarity)} flex items-center gap-4`}>
              <div className="w-16 h-16 rounded-full border-4 border-current flex items-center justify-center font-bold text-2xl">
                {scanResult.overall_similarity}%
              </div>
              <div>
                <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">Turnitin Index</div>
                <div className="text-lg font-bold text-white">Overall Similarity</div>
                <div className="text-xs text-slate-400 mt-0.5">
                  {scanResult.overall_similarity > 30 ? 'High similarity detected' : 'Acceptable academic range'}
                </div>
              </div>
            </div>

            {/* Exact Matching */}
            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Layer 1 Matching</span>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold text-rose-400">{scanResult.exact_similarity}%</span>
                <span className="text-xs text-slate-400">Exact Shingles</span>
              </div>
              <p className="text-xs text-slate-500">Locality-Sensitive Hashing & Rabin-Karp</p>
            </div>

            {/* Paraphrase Matching */}
            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Layer 2 Matching</span>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold text-amber-400">{scanResult.paraphrase_similarity}%</span>
                <span className="text-xs text-slate-400">Reworded / Paraphrased</span>
              </div>
              <p className="text-xs text-slate-500">Dense Semantic Embeddings & Cosine</p>
            </div>

            {/* Filters Applied */}
            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Protected Spans</span>
              <div className="text-xs space-y-1.5 text-slate-300">
                <div className="flex justify-between">
                  <span>Quotes Excluded:</span>
                  <span className="font-semibold text-emerald-400">{scanResult.quotes_found}</span>
                </div>
                <div className="flex justify-between">
                  <span>Bibliography Excluded:</span>
                  <span className="font-semibold text-emerald-400">
                    {scanResult.bibliography_excluded ? 'Yes (Cleaned)' : 'No'}
                  </span>
                </div>
              </div>
              <p className="text-[11px] text-slate-500">False-positive safeguards active</p>
            </div>
          </div>

          {/* Interactive Document Viewer & Source Breakdown */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Highlighted Document Viewer */}
            <div className="lg:col-span-2 bg-slate-900/90 rounded-2xl border border-slate-800 p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-base font-semibold text-white flex items-center gap-2">
                  <span>Document Highlight Inspection</span>
                  <span className="text-xs font-normal text-slate-400">(Click any highlight for source match)</span>
                </h3>

                <div className="flex items-center gap-3 text-xs">
                  <span className="flex items-center gap-1.5 text-rose-300">
                    <span className="w-3 h-3 rounded bg-rose-500/40 border border-rose-500 inline-block" />
                    Exact Match
                  </span>
                  <span className="flex items-center gap-1.5 text-amber-300">
                    <span className="w-3 h-3 rounded bg-amber-500/40 border border-amber-500 inline-block" />
                    Paraphrase
                  </span>
                </div>
              </div>

              {renderHighlightedDocument()}

              {/* Action Bridge to Humanizer */}
              {scanResult.overall_similarity > 10 && (
                <div className="mt-4 p-4 rounded-xl bg-purple-950/40 border border-purple-800/60 flex items-center justify-between">
                  <div>
                    <div className="text-sm font-semibold text-purple-200 flex items-center gap-1.5">
                      <Sparkles className="w-4 h-4 text-purple-400" />
                      Rewrite & Humanize Plagiarized Document
                    </div>
                    <div className="text-xs text-purple-300/80 mt-0.5">
                      Send this text to the AI Humanizer to restructure sentences and bypass similarity flags.
                    </div>
                  </div>
                  <button
                    onClick={() => onSendToHumanizer(scanResult.raw_text)}
                    className="flex items-center gap-1.5 px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg text-xs font-semibold transition"
                  >
                    <span>Send to Humanizer</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}
            </div>

            {/* Source Matches & Inspector Drawer */}
            <div className="space-y-4">
              {/* Selected Span Match Detail */}
              {selectedSpan ? (
                <div className="bg-slate-900 rounded-2xl border border-indigo-700/60 p-5 shadow-xl animate-fadeIn">
                  <div className="flex justify-between items-start mb-3">
                    <span className={`text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded ${
                      selectedSpan.match_type === 'exact' ? 'bg-rose-950 text-rose-300 border border-rose-800' : 'bg-amber-950 text-amber-300 border border-amber-800'
                    }`}>
                      {selectedSpan.match_type === 'exact' ? 'Exact Match (100%)' : `Paraphrase (${Math.round(selectedSpan.similarity * 100)}%)`}
                    </span>
                    <button
                      onClick={() => setSelectedSpan(null)}
                      className="text-slate-400 hover:text-white"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>

                  <h4 className="text-sm font-semibold text-white mb-1">{selectedSpan.source_title}</h4>
                  <p className="text-xs text-slate-400 mb-3">{selectedSpan.source_author}</p>

                  <div className="space-y-2 text-xs">
                    <div>
                      <span className="text-slate-400 font-medium">Your text:</span>
                      <div className="mt-1 p-2 bg-slate-950 rounded border border-slate-800 text-slate-200">
                        "{selectedSpan.text}"
                      </div>
                    </div>
                    <div>
                      <span className="text-slate-400 font-medium">Matched source passage:</span>
                      <div className="mt-1 p-2 bg-slate-950 rounded border border-slate-800 text-slate-300 italic">
                        "{selectedSpan.matched_snippet}"
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-4 bg-slate-900/40 rounded-xl border border-slate-800 text-xs text-slate-400 text-center">
                  Click any highlighted sentence on the left to inspect its matched source passage.
                </div>
              )}

              {/* Source Breakdown List */}
              <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-5">
                <h4 className="text-sm font-semibold text-white mb-3">Ranked Source Breakdown</h4>
                {scanResult.source_breakdown.length === 0 ? (
                  <div className="text-xs text-slate-500 py-3 text-center">No reference source overlaps.</div>
                ) : (
                  <div className="space-y-3">
                    {scanResult.source_breakdown.map((src, i) => (
                      <div
                        key={i}
                        className="p-3 bg-slate-950/80 rounded-xl border border-slate-800/80 flex items-center justify-between"
                      >
                        <div className="truncate pr-2">
                          <p className="text-xs font-semibold text-slate-200 truncate">{src.source_title}</p>
                          <span className="text-[11px] text-slate-500">Reference Corpus Match</span>
                        </div>
                        <div className="text-right shrink-0">
                          <span className="text-sm font-bold text-rose-400">{src.percentage}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
