import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BASE_DIR / "data" / "uploads"
CORPUS_DIR = BASE_DIR / "data" / "corpus"
EXPORTS_DIR = BASE_DIR / "data" / "exports"

for directory in [UPLOADS_DIR, CORPUS_DIR, EXPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

DEFAULT_MIN_SHINGLE_SIZE = 5  # 5-word shingles for exact matching
DEFAULT_SHINGLE_MAX = 7
EXACT_MATCH_THRESHOLD = 0.85
PARAPHRASE_SIMILARITY_THRESHOLD = 0.70

# Default local LLM endpoints
DEFAULT_OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
DEFAULT_VLLM_URL = os.getenv("VLLM_URL", "http://localhost:8000/v1")
