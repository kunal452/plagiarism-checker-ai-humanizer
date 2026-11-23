import os
import uuid
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel

from .ingestion.parser import DocumentParser
from .plagiarism.fingerprint import FingerprintEngine
from .plagiarism.vector_engine import SemanticVectorEngine
from .plagiarism.corpus import ReferenceCorpusManager
from .plagiarism.detector import PlagiarismDetector
from .humanizer.engine import HumanizerEngine
from .humanizer.ai_detector import AIDetectorScorer
from .export.exporter import DocumentExporter

app = FastAPI(
    title="Veritas AI - Plagiarism Checker & Unlimited AI Humanizer",
    version="1.0.0",
    description="Dual-pipeline Turnitin-style plagiarism detection with chunked LLM humanization"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
vector_engine = SemanticVectorEngine()
corpus_manager = ReferenceCorpusManager(vector_engine)
plagiarism_detector = PlagiarismDetector(corpus_manager, vector_engine)
humanizer_engine = HumanizerEngine()

# Pydantic Schemas
class PlagiarismCheckRequest(BaseModel):
    text: str
    exclude_quotes: bool = True
    exclude_bibliography: bool = True
    min_shingle_size: int = 5
    paraphrase_threshold: float = 0.68

class CorpusAddRequest(BaseModel):
    title: str
    content: str
    source_type: str = "Research Paper"
    author: Optional[str] = "Independent Author"

class HumanizeRequest(BaseModel):
    text: str
    mode: str = "academic"  # "academic", "conversational", "professional", "creative"
    backend: str = "auto"   # "auto", "ollama", "vllm", "algorithmic"
    model_name: Optional[str] = None
    temperature: float = 0.70
    burstiness_level: str = "balanced"  # "subtle", "balanced", "aggressive"
    preserve_citations: bool = True

class AIScoreRequest(BaseModel):
    text: str

class ExportRequest(BaseModel):
    text: str
    title: Optional[str] = "Humanized Document"

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Veritas AI Engine",
        "indexed_documents": len(corpus_manager.documents),
        "version": "1.0.0"
    }

# ----------------- Document Parsing Endpoint -----------------
@app.post("/api/documents/parse")
async def parse_document(file: UploadFile = File(...)):
    content = await file.read()
    try:
        parsed = DocumentParser.parse_file(file.filename, content)
        return parsed
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse document: {str(e)}")

# ----------------- Plagiarism Endpoints -----------------
@app.post("/api/plagiarism/check")
async def check_plagiarism(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    exclude_quotes: bool = Form(True),
    exclude_bibliography: bool = Form(True),
    min_shingle_size: int = Form(5),
    paraphrase_threshold: float = Form(0.68)
):
    target_text = ""
    filename = "Pasted Text"
    if file:
        content = await file.read()
        parsed = DocumentParser.parse_file(file.filename, content)
        target_text = parsed.get("text", "")
        filename = file.filename
    elif text:
        target_text = text

    if not target_text.strip():
        raise HTTPException(status_code=400, detail="No text or document provided for analysis")

    results = plagiarism_detector.scan_document(
        raw_text=target_text,
        exclude_quotes=exclude_quotes,
        exclude_bibliography=exclude_bibliography,
        min_shingle_size=min_shingle_size,
        paraphrase_threshold=paraphrase_threshold
    )
    results["filename"] = filename
    results["raw_text"] = target_text
    return results

@app.get("/api/plagiarism/corpus")
def get_corpus():
    return {
        "count": len(corpus_manager.documents),
        "documents": corpus_manager.get_all_documents()
    }

@app.post("/api/plagiarism/corpus")
def add_to_corpus(req: CorpusAddRequest):
    if not req.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")
    doc_id = f"user-{uuid.uuid4().hex[:8]}"
    doc = corpus_manager.index_document(
        doc_id=doc_id,
        title=req.title,
        content=req.content,
        source_type=req.source_type,
        author=req.author,
        persist=True
    )
    return {"message": "Document indexed successfully", "document": doc}

# ----------------- AI Humanizer Endpoints -----------------
@app.post("/api/humanize/process")
async def humanize_text(req: HumanizeRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    result = await humanizer_engine.humanize_document(
        raw_text=req.text,
        mode=req.mode,
        backend=req.backend,
        model_name=req.model_name,
        temperature=req.temperature,
        burstiness_level=req.burstiness_level,
        preserve_citations=req.preserve_citations
    )
    return result

@app.post("/api/humanize/ai-score")
def get_ai_score(req: AIScoreRequest):
    metrics = AIDetectorScorer.evaluate(req.text)
    return metrics

# ----------------- Document Export Endpoints -----------------
@app.post("/api/export/docx")
def export_docx(req: ExportRequest):
    docx_bytes = DocumentExporter.export_to_docx(req.text, title=req.title or "Humanized Document")
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": 'attachment; filename="humanized_document.docx"'}
    )

@app.post("/api/export/pdf")
def export_pdf(req: ExportRequest):
    pdf_bytes = DocumentExporter.export_to_pdf(req.text, title=req.title or "Humanized Document")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="humanized_document.pdf"'}
    )

# ----------------- Serve Frontend Static Build -----------------
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api"):
            raise HTTPException(status_code=404, detail="API route not found")
        file_path = FRONTEND_DIST / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")

