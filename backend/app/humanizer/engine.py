import os
import re
import httpx
from typing import Dict, Any, List, Optional
from ..ingestion.chunker import TextChunker
from .cliches import AIClicheSanitizer
from .burstiness import BurstinessTransformer
from .fact_guard import FactGuard
from .restitcher import ChunkRestitcher
from .ai_detector import AIDetectorScorer

SYSTEM_PROMPT_HUMANIZER = """You are an expert human author and prose editor. 
Your job is to rewrite the provided text so that it reads completely naturally, as if written by an insightful human writer, bypassing formulaic AI detector patterns.

STRICT INSTRUCTIONS:
1. Vary sentence length dramatically (burstiness): Alternate between short, punchy 3-7 word sentences and longer, nuanced explanations with varied clauses.
2. Avoid uniform cadences and predictable transitions.
3. NEVER use generic AI markers or clichés, such as: "delve", "moreover", "furthermore", "in conclusion", "rich tapestry", "testament to", "multifaceted", "pivotal", "beacon", "it is important to note".
4. Use active voice and concrete verbs instead of passive, abstract constructions.
5. PRESERVE TECHNICAL ACCURACY: Do not alter numbers, dates, percentages, citations, formulas, or proper nouns. Keep all key factual claims completely intact.
6. Return ONLY the rewritten text without preambles, greetings, or conversational remarks.
"""

MODE_GUIDELINES = {
    "academic": "Tone: Academic and scholarly yet direct. Maintain rigorous terminology, passive-to-active balance, and precise vocabulary.",
    "conversational": "Tone: Engaging, relatable, and clear. Write like an experienced professional speaking to a curious colleague.",
    "professional": "Tone: Executive, crisp, and persuasive. Focus on efficiency, direct action, and impactful insights.",
    "creative": "Tone: Vivid, rhythmically diverse, and memorable. Use inventive phrasing and evocative pacing."
}

class HumanizerEngine:
    """
    Unlimited AI-Text Humanizer Engine:
    - Chunking for long files (400-500 words)
    - Perplexity & Burstiness variation
    - Fact Guard & Citation protection
    - Multi-backend LLM support (Ollama, vLLM, OpenAI-compatible, Smart Heuristic fallback)
    """

    def __init__(self, ollama_url: str = "http://localhost:11434", vllm_url: str = "http://localhost:8000/v1"):
        self.ollama_url = ollama_url
        self.vllm_url = vllm_url

    async def rewrite_with_ollama(self, prompt: str, model: str = "llama3:8b", temperature: float = 0.7) -> Optional[str]:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "system": SYSTEM_PROMPT_HUMANIZER,
                        "options": {"temperature": temperature},
                        "stream": False
                    }
                )
                if res.status_code == 200:
                    return res.json().get("response", "").strip()
        except Exception:
            return None
        return None

    async def rewrite_with_vllm(self, text: str, model: str = "mistralai/Mistral-7B-Instruct-v0.3", temperature: float = 0.7, api_key: str = "EMPTY") -> Optional[str]:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(
                    f"{self.vllm_url}/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT_HUMANIZER},
                            {"role": "user", "content": text}
                        ],
                        "temperature": temperature,
                        "max_tokens": 1500
                    }
                )
                if res.status_code == 200:
                    return res.json()["choices"][0]["message"]["content"].strip()
        except Exception:
            return None
        return None

    def algorithmic_humanize(self, text: str, mode: str = "academic", burstiness_level: str = "balanced") -> str:
        """
        High-grade algorithmic humanizer:
        Performs lexical sanitization, burstiness modulation, active voice adjustments,
        and natural syntax perturbations. Works with 100% reliability offline without external LLM.
        """
        # 1. Clean AI clichés
        sanitized, _ = AIClicheSanitizer.sanitize(text)

        # 2. Split into paragraphs
        paragraphs = [p.strip() for p in sanitized.split("\n\n") if p.strip()]
        transformed_paras = []

        for p in paragraphs:
            # Split into sentences
            raw_sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', p) if s.strip()]
            
            # Apply burstiness transformation
            bursty_sents = BurstinessTransformer.inject_rhythm_variation(raw_sents, intensity=burstiness_level)

            # Apply stylistic nuances based on mode
            para_text = " ".join(bursty_sents)
            if mode == "conversational":
                para_text = re.sub(r'\butilize\b', 'use', para_text, flags=re.IGNORECASE)
                para_text = re.sub(r'\bcommence\b', 'start', para_text, flags=re.IGNORECASE)
                para_text = re.sub(r'\bfacilitate\b', 'help with', para_text, flags=re.IGNORECASE)
            elif mode == "professional":
                para_text = re.sub(r'\bvery important\b', 'critical', para_text, flags=re.IGNORECASE)
                para_text = re.sub(r'\ba lot of\b', 'substantial', para_text, flags=re.IGNORECASE)

            transformed_paras.append(para_text)

        return "\n\n".join(transformed_paras)

    async def humanize_document(
        self,
        raw_text: str,
        mode: str = "academic",
        backend: str = "auto",  # "auto", "ollama", "vllm", "algorithmic"
        custom_endpoint: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        burstiness_level: str = "balanced",
        preserve_citations: bool = True
    ) -> Dict[str, Any]:
        """
        End-to-end humanizer pipeline:
        1. Evaluates original AI probability & burstiness.
        2. Chunks document into 400-500 word segments.
        3. Humanizes each chunk using selected backend.
        4. Re-stitches and smooths boundaries.
        5. Validates fact fidelity via FactGuard.
        6. Computes post-humanization AI probability and diff.
        """
        if not raw_text.strip():
            return {
                "original_text": "",
                "humanized_text": "",
                "original_metrics": {},
                "humanized_metrics": {},
                "chunks_processed": 0,
                "fidelity": {},
                "backend_used": "none"
            }

        # Step 1: Pre-evaluation
        original_metrics = AIDetectorScorer.evaluate(raw_text)

        # Step 2: Chunking for long files
        chunks = TextChunker.create_humanizer_chunks(raw_text, target_words=450, overlap_words=30)
        rewritten_chunks = []
        backend_used = backend

        for chunk in chunks:
            c_text = chunk["text"]
            rewritten_text = None

            # Attempt LLM if requested or auto
            if backend in ["ollama", "auto"]:
                m = model_name or "llama3:8b"
                rewritten_text = await self.rewrite_with_ollama(c_text, model=m, temperature=temperature)
                if rewritten_text:
                    backend_used = f"Ollama ({m})"

            if not rewritten_text and backend in ["vllm", "auto"]:
                m = model_name or "mistralai/Mistral-7B-Instruct-v0.3"
                rewritten_text = await self.rewrite_with_vllm(c_text, model=m, temperature=temperature)
                if rewritten_text:
                    backend_used = f"vLLM ({m})"

            # Fallback to smart algorithmic humanizer
            if not rewritten_text:
                rewritten_text = self.algorithmic_humanize(c_text, mode=mode, burstiness_level=burstiness_level)
                if backend_used == "auto":
                    backend_used = "Algorithmic Burstiness Engine (Offline)"

            rewritten_chunks.append({
                "chunk_id": chunk["chunk_id"],
                "text": rewritten_text
            })

        # Step 4: Re-stitching & transition smoothing
        full_humanized = ChunkRestitcher.restitch_chunks(rewritten_chunks)

        # Step 5: Fact Guard audit
        fidelity = FactGuard.audit_fidelity(raw_text, full_humanized)
        if preserve_citations and not fidelity["is_faithful"]:
            full_humanized = FactGuard.restore_missing_citations(raw_text, full_humanized)
            fidelity = FactGuard.audit_fidelity(raw_text, full_humanized)

        # Step 6: Post-evaluation
        humanized_metrics = AIDetectorScorer.evaluate(full_humanized)

        return {
            "original_text": raw_text,
            "humanized_text": full_humanized,
            "original_metrics": original_metrics,
            "humanized_metrics": humanized_metrics,
            "chunks_processed": len(chunks),
            "fidelity": fidelity,
            "backend_used": backend_used,
            "mode": mode,
            "burstiness_level": burstiness_level
        }
