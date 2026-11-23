# Veritas AI: Turnitin-Style Plagiarism Checker & Unlimited AI Humanizer

A production-ready, dual-pipeline system combining a **Turnitin-style Plagiarism Detection Engine** with an **Unlimited AI-Text Humanizer and Paraphrasing Studio**.

---

## 🏛️ System Architecture

```
                                  USER DOCUMENT
                     (PDF via PyMuPDF / Word via python-docx / Text)
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │   Document Ingestion &      │
                         │   False-Positive Cleaner    │
                         └──────────────┬──────────────┘
                                        │
                 ┌──────────────────────┴──────────────────────┐
                 ▼                                             ▼
  ┌─────────────────────────────┐               ┌─────────────────────────────┐
  │   PIPELINE 1: PLAGIARISM    │               │    PIPELINE 2: HUMANIZER    │
  │   Dual-Layer Matching       │               │    Chunked LLM Rewriter     │
  └──────────────┬──────────────┘               └──────────────┬──────────────┘
                 │                                             │
      ┌──────────┴──────────┐                       ┌──────────┴──────────┐
      ▼                     ▼                       ▼                     ▼
┌───────────┐         ┌───────────┐           ┌───────────┐         ┌───────────┐
│  Layer 1: │         │  Layer 2: │           │ 400-Word  │         │Perplexity │
│ MinHash & │         │  Semantic │           │ Chunking  │         │& Burst    │
│Rabin-Karp │         │  Vectors  │           │ & Overlap │         │Modulation │
│(5-7 words)│         │(Cosine Sim│           └─────┬─────┘         └─────┬─────┘
└─────┬─────┘         └─────┬─────┘                 │                     │
      └──────────┬──────────┘                       └──────────┬──────────┘
                 ▼                                             ▼
  ┌─────────────────────────────┐               ┌─────────────────────────────┐
  │ Turnitin Circular Score &   │               │ FactGuard & Re-stitcher     │
  │ Highlighted Span Inspector  │               │ (Fidelity & Transitions)    │
  └─────────────────────────────┘               └──────────────┬──────────────┘
                                                               │
                                                               ▼
                                                ┌─────────────────────────────┐
                                                │ Side-by-Side Diff Studio    │
                                                │ & PDF/DOCX Download Export  │
                                                └─────────────────────────────┘
```

---

## 🚀 Key Modules & Tech Stack

| Module | Tech Stack | Role & Implementation |
| :--- | :--- | :--- |
| **Frontend** | React 19 + Tailwind CSS + Lucide Icons + `diff` | Dropzone, Turnitin radial similarity gauge, interactive highlighted spans, split-screen live diff viewer |
| **Backend API** | Python (FastAPI + Uvicorn) | Async parsing, dual-layer plagiarism matching, chunked rewriter, REST endpoints |
| **File Parsing** | PyMuPDF (fitz) + python-docx | High-fidelity extraction preserving paragraph structure, page counts, and bounding coordinates |
| **Fingerprint Engine** | MinHash + LSH + Rabin-Karp | 5–7 word shingles with 64 hash permutations for exact copy-paste detection at scale |
| **Vector Engine** | Dense Semantic Vectors + Cosine Similarity | Catches paraphrased and reworded plagiarism above tunable threshold (default: 0.68) |
| **Corpus Manager** | Persistent JSON + In-Memory Index | Pre-indexed academic papers, past student submissions, and instant custom indexing |
| **AI Humanizer** | Self-hosted Ollama / vLLM / Smart Heuristic Engine | Eliminates AI clichés (`delve`, `moreover`, etc.), injects burstiness, and prevents token limits |
| **FactGuard** | Regex & Entity Validator | Prevents semantic drift by auditing and protecting numbers, dates, statistics, and citations (`[1]`, `(Smith, 2024)`) |
| **Exporter** | PyMuPDF + python-docx | One-click export of rewritten clean documents to `.docx` and `.pdf` |

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.10+ (tested with Python 3.14)
- Node.js 18+ & npm

### 2. Launching Both Servers in One Command
Simply run:
```bash
python run_all.py
```
*(Or double-click `start.bat` on Windows)*

- **Web UI**: [http://localhost:5173](http://localhost:5173)
- **API Documentation (Swagger UI)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🔍 Step-by-Step Feature Walkthrough

### 1. Document Ingestion & False-Positive Filters
- **Quotation Exclusion**: Turnitin standard feature. Any text enclosed within `"..."`, `“...”`, or `‘...’` is identified and can be excluded so cited quotes do not trigger plagiarism flags.
- **Bibliography Stripping**: Automatically recognizes `References`, `Works Cited`, or `Bibliography` headings in the document and isolates them to prevent false positive matches.
- **Format Support**: Direct support for `.pdf` (via PyMuPDF), `.docx` (via python-docx), and `.txt`.

### 2. Dual-Layer Plagiarism Detection
- **Layer 1 (Exact & Near-Exact)**:
  - Tokenizes text into lowercase normalized shingles (5–7 words).
  - Computes a 64-permutation MinHash signature for rapid Locality-Sensitive Hashing.
  - Applies Rabin-Karp polynomial rolling hashing to identify exact character coordinates for highlighted rendering.
- **Layer 2 (Paraphrase & Rewording Detection)**:
  - Generates sliding 3-sentence evaluation windows.
  - Compares dense semantic representations using Cosine Similarity against the reference corpus.
  - Distinguishes between exact matches (similarity $\ge 0.92$) and paraphrased overlaps ($0.68 \le \text{sim} < 0.92$).
- **Turnitin-Style Report**:
  - Circular Similarity Index Gauge.
  - Interactive highlighted spans (Red = Exact, Amber = Paraphrase).
  - Click any highlighted span to view the side-by-side comparison with the matched source.
  - Ranked source breakdown list with individual percentage contributions.

### 3. Unlimited AI-Text Humanizer Studio
- **Chunking for Unlimited Length**:
  - Files and books are segmented into ~450-word chunks with overlapping context, completely bypassing LLM context window constraints and eliminating third-party API costs.
- **Burstiness & Perplexity Tuning**:
  - LLM detectors rely on uniform sentence lengths (low burstiness) and predictable n-grams (low perplexity).
  - The humanizer mixes staccato punchy sentences (3-7 words) with compound, nuanced sentences.
- **AI Cliché Purge**:
  - Strips hallmark LLM words: `delve`, `tapestry`, `moreover`, `furthermore`, `in conclusion`, `beacon`, `pivotal role`, `testament to`, `multifaceted`.
- **FactGuard**:
  - Audits numbers, metrics, dates, and citation tags (`[1]`, `[1-3]`, `(Author, Year)`).
  - Guarantees zero semantic drift.
- **Split-Screen Studio**:
  - Original AI Draft vs. Humanized Output side-by-side.
  - AI Detection Probability meter before and after (e.g. 99% AI $\rightarrow$ 6% AI).
  - Live Word-Level Diff Viewer showing green insertions and struck-through deletions.
  - Instant re-download as `.docx` or `.pdf`.
  - 1-click **"Verify in Plagiarism Checker"** bridge.

---

## 🛠️ REST API Reference

| Endpoint | Method | Parameters | Description |
| :--- | :--- | :--- | :--- |
| `/api/health` | `GET` | - | Service health check and corpus count |
| `/api/documents/parse` | `POST` | `file` (multipart) | Parses PDF or DOCX and extracts clean text |
| `/api/plagiarism/check` | `POST` | `text`, `file`, `exclude_quotes`, `exclude_bibliography`, `min_shingle_size` | Runs dual-layer plagiarism analysis |
| `/api/plagiarism/corpus` | `GET` | - | Lists all indexed reference documents |
| `/api/plagiarism/corpus` | `POST` | `title`, `author`, `content`, `source_type` | Indexes a new reference paper |
| `/api/humanize/process` | `POST` | `text`, `mode`, `backend`, `burstiness_level`, `preserve_citations` | Runs chunked rewriter & burstiness tuning |
| `/api/humanize/ai-score` | `POST` | `text` | Evaluates AI probability, perplexity, and burstiness |
| `/api/export/docx` | `POST` | `text`, `title` | Generates formatted Word `.docx` download |
| `/api/export/pdf` | `POST` | `text`, `title` | Generates formatted `.pdf` download |

---

## 🧪 Automated Verification Test Suite

To run the end-to-end integration test suite:
```bash
python test_system.py
```
Outputs validation across document parsing, false-positive quotation exclusion, MinHash 64-bit signature generation, exact copy detection, clean-text negative controls, AI probability metrics, and PDF/DOCX exporters.
