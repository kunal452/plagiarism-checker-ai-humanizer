import React, { useMemo } from 'react';
import * as Diff from 'diff';

export default function DiffViewer({ originalText, modifiedText }) {
  const diffParts = useMemo(() => {
    if (!originalText || !modifiedText) return [];
    return Diff.diffWordsWithSpace(originalText, modifiedText);
  }, [originalText, modifiedText]);

  return (
    <div className="p-4 bg-slate-950/80 rounded-xl border border-slate-800 text-sm font-mono leading-relaxed whitespace-pre-wrap max-h-[500px] overflow-y-auto">
      {diffParts.map((part, index) => {
        if (part.added) {
          return (
            <span
              key={index}
              className="bg-emerald-950/80 text-emerald-300 font-semibold px-1 py-0.5 rounded border border-emerald-700/60"
            >
              {part.value}
            </span>
          );
        }
        if (part.removed) {
          return (
            <span
              key={index}
              className="bg-rose-950/80 text-rose-400 line-through px-1 py-0.5 rounded border border-rose-800/60 opacity-70"
            >
              {part.value}
            </span>
          );
        }
        return <span key={index} className="text-slate-300">{part.value}</span>;
      })}
    </div>
  );
}
