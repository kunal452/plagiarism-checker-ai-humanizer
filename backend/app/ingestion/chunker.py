import re
from typing import List, Dict, Any

class TextChunker:
    """
    Handles sentence segmentation, overlapping sliding windows, and character-offset tracking.
    """

    SENTENCE_SPLIT_REGEX = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9"“‘])')

    @classmethod
    def split_sentences(cls, text: str) -> List[Dict[str, Any]]:
        """
        Splits text into sentences while tracking exact character offsets.
        """
        sentences = []
        if not text.strip():
            return sentences

        # Use regex to find sentence boundaries
        splits = [0]
        for m in cls.SENTENCE_SPLIT_REGEX.finditer(text):
            splits.append(m.start() + 1)
        splits.append(len(text))

        for i in range(len(splits) - 1):
            start = splits[i]
            end = splits[i + 1]
            raw_chunk = text[start:end]
            clean_s = raw_chunk.strip()
            if clean_s:
                # Adjust start to first non-whitespace
                adjusted_start = start + (len(raw_chunk) - len(raw_chunk.lstrip()))
                adjusted_end = adjusted_start + len(clean_s)
                sentences.append({
                    "sentence_idx": len(sentences),
                    "text": clean_s,
                    "start": adjusted_start,
                    "end": adjusted_end
                })

        return sentences

    @classmethod
    def create_sliding_windows(cls, text: str, window_size: int = 3, step_size: int = 1) -> List[Dict[str, Any]]:
        """
        Creates overlapping 3-sentence windows for dual-layer plagiarism matching.
        """
        sentences = cls.split_sentences(text)
        if not sentences:
            return []

        chunks = []
        num_sentences = len(sentences)

        if num_sentences <= window_size:
            start_char = sentences[0]["start"]
            end_char = sentences[-1]["end"]
            combined_text = text[start_char:end_char]
            chunks.append({
                "chunk_idx": 0,
                "text": combined_text,
                "start": start_char,
                "end": end_char,
                "sentence_count": num_sentences,
                "word_count": len(combined_text.split())
            })
            return chunks

        for i in range(0, num_sentences - window_size + 1, step_size):
            window_sentences = sentences[i : i + window_size]
            start_char = window_sentences[0]["start"]
            end_char = window_sentences[-1]["end"]
            combined_text = text[start_char:end_char]
            chunks.append({
                "chunk_idx": len(chunks),
                "text": combined_text,
                "start": start_char,
                "end": end_char,
                "sentence_count": len(window_sentences),
                "word_count": len(combined_text.split())
            })

        return chunks

    @classmethod
    def create_humanizer_chunks(cls, text: str, target_words: int = 400, overlap_words: int = 40) -> List[Dict[str, Any]]:
        """
        Splits long essays/books into ~400-500 word segments with semantic overlap
        so LLM context limits are never breached and boundary coherence is preserved.
        """
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks = []
        current_paras = []
        current_word_count = 0
        chunk_idx = 0

        for p in paragraphs:
            p_words = len(p.split())
            if current_word_count + p_words > target_words and current_paras:
                chunk_text = "\n\n".join(current_paras)
                chunks.append({
                    "chunk_id": chunk_idx,
                    "text": chunk_text,
                    "word_count": current_word_count,
                    "paragraphs_count": len(current_paras)
                })
                chunk_idx += 1
                # Keep last paragraph for overlap context if substantial
                if len(current_paras) > 1 and len(current_paras[-1].split()) <= overlap_words:
                    current_paras = [current_paras[-1], p]
                    current_word_count = len(current_paras[0].split()) + p_words
                else:
                    current_paras = [p]
                    current_word_count = p_words
            else:
                current_paras.append(p)
                current_word_count += p_words

        if current_paras:
            chunks.append({
                "chunk_id": chunk_idx,
                "text": "\n\n".join(current_paras),
                "word_count": current_word_count,
                "paragraphs_count": len(current_paras)
            })

        return chunks
