from typing import List, Dict, Any
import re

class ChunkRestitcher:
    """
    Re-stitches independently rewritten chunks into a seamless, cohesive document.
    Executes a transition smoothing pass across paragraph boundaries.
    """

    TRANSITION_SMOOTHERS = [
        (re.compile(r'\n{3,}'), '\n\n'),  # Normalize excessive spacing
        (re.compile(r'([.!?])\s*([a-z])'), lambda m: f"{m.group(1)} {m.group(2).upper()}"), # Fix casing
        (re.compile(r'\s+([,.:;?!])'), r'\1'), # Fix stray spaces before punctuation
        (re.compile(r'([—–])\s+'), r'\1 '),    # Clean dash spacing
    ]

    @classmethod
    def restitch_chunks(cls, rewritten_chunks: List[Dict[str, Any]]) -> str:
        """
        Merges chunk texts and applies boundary smoothing.
        """
        if not rewritten_chunks:
            return ""

        # Sort chunks by order
        sorted_chunks = sorted(rewritten_chunks, key=lambda c: c.get("chunk_id", 0))
        assembled_texts = []

        for chunk in sorted_chunks:
            t = chunk.get("text", "").strip()
            if t:
                assembled_texts.append(t)

        full_doc = "\n\n".join(assembled_texts)

        # Apply smoothing passes
        for pattern, replacement in cls.TRANSITION_SMOOTHERS:
            if callable(replacement):
                full_doc = pattern.sub(replacement, full_doc)
            else:
                full_doc = pattern.sub(replacement, full_doc)

        return full_doc.strip()
