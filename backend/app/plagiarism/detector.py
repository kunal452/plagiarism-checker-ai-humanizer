from typing import List, Dict, Any, Optional
from .fingerprint import FingerprintEngine
from .vector_engine import SemanticVectorEngine
from .corpus import ReferenceCorpusManager
from ..ingestion.cleaner import DocumentCleaner
from ..ingestion.chunker import TextChunker

class PlagiarismDetector:
    """
    Turnitin-style Dual-Layer Plagiarism Detection Engine:
    Layer 1: Exact & Near-Exact Matching (5-7 word n-grams, Rabin-Karp, MinHash).
    Layer 2: Paraphrase & Rewording Detection (Dense semantic vectors, cosine similarity).
    Includes smart filters for quotation exclusion and bibliography stripping.
    """

    def __init__(self, corpus_manager: ReferenceCorpusManager, vector_engine: SemanticVectorEngine):
        self.corpus_manager = corpus_manager
        self.vector_engine = vector_engine

    def scan_document(
        self,
        raw_text: str,
        exclude_quotes: bool = True,
        exclude_bibliography: bool = True,
        min_shingle_size: int = 5,
        paraphrase_threshold: float = 0.68
    ) -> Dict[str, Any]:
        """
        Executes comprehensive dual-layer plagiarism scan on input document.
        """
        if not raw_text.strip():
            return {
                "overall_similarity": 0.0,
                "exact_similarity": 0.0,
                "paraphrase_similarity": 0.0,
                "total_words": 0,
                "matched_words": 0,
                "matched_spans": [],
                "source_breakdown": [],
                "clean_metadata": {}
            }

        # 1. Clean document and detect structural elements
        cleaned = DocumentCleaner.clean_document(raw_text)
        analysis_text = cleaned["body_text"] if exclude_bibliography else cleaned["full_text"]
        quotes = cleaned["quotations"]
        total_words = len(analysis_text.split())

        if total_words == 0:
            return {
                "overall_similarity": 0.0,
                "exact_similarity": 0.0,
                "paraphrase_similarity": 0.0,
                "total_words": 0,
                "matched_words": 0,
                "matched_spans": [],
                "source_breakdown": [],
                "clean_metadata": cleaned
            }

        # Helper to check if a span is inside a quotation
        def is_quoted(start_c: int, end_c: int) -> bool:
            for q in quotes:
                if (q["start"] <= start_c < q["end"]) or (q["start"] < end_c <= q["end"]):
                    return True
            return False

        all_matches: List[Dict[str, Any]] = []
        source_matched_words: Dict[str, set] = {}

        # 2. LAYER 1: Exact & Near-Exact Matching using Shingles & Rabin-Karp
        for doc_id, doc in self.corpus_manager.documents.items():
            exact_spans = FingerprintEngine.find_exact_matching_spans(
                analysis_text,
                doc["content"],
                k=min_shingle_size
            )

            for span in exact_spans:
                s_start = span["query_start"]
                s_end = span["query_end"]
                in_quote = is_quoted(s_start, s_end)

                if exclude_quotes and in_quote:
                    continue  # skip properly quoted text

                matched_str = span["text"]
                words_in_span = len(matched_str.split())

                all_matches.append({
                    "start": s_start,
                    "end": s_end,
                    "text": matched_str,
                    "source_id": doc_id,
                    "source_title": doc["title"],
                    "source_author": doc.get("author", "Academic Reference"),
                    "match_type": "exact",
                    "similarity": 1.0,
                    "is_quoted": in_quote,
                    "words_count": words_in_span,
                    "matched_snippet": doc["content"][span["source_start"]:span["source_end"]]
                })

                source_matched_words.setdefault(doc["title"], set()).update(range(s_start, s_end))

        # 3. LAYER 2: Paraphrase & Rewording Detection using Semantic Vectors
        # Query 3-sentence sliding windows against the vector index
        windows = TextChunker.create_sliding_windows(analysis_text, window_size=2, step_size=1)
        for w in windows:
            w_start = w["start"]
            w_end = w["end"]
            in_quote = is_quoted(w_start, w_end)

            if exclude_quotes and in_quote:
                continue

            # Check if this span is already fully covered by an exact match
            already_exact = any(
                m["match_type"] == "exact" and m["start"] <= w_start and m["end"] >= w_end
                for m in all_matches
            )
            if already_exact:
                continue

            vector_hits = self.vector_engine.query_similarity(
                w["text"],
                top_k=2,
                threshold=paraphrase_threshold
            )

            for hit in vector_hits:
                # If high semantic similarity but low exact match, it is a paraphrase
                all_matches.append({
                    "start": w_start,
                    "end": w_end,
                    "text": w["text"],
                    "source_id": hit["doc_id"],
                    "source_title": hit["doc_title"],
                    "source_author": "Indexed Reference",
                    "match_type": hit["match_type"],
                    "similarity": hit["similarity"],
                    "is_quoted": in_quote,
                    "words_count": len(w["text"].split()),
                    "matched_snippet": hit["source_text"]
                })
                source_matched_words.setdefault(hit["doc_title"], set()).update(range(w_start, w_end))

        # 4. Calculate Turnitin-style Overall Similarity %
        # Union of all matched character positions
        matched_char_positions = set()
        exact_char_positions = set()
        paraphrase_char_positions = set()

        for m in all_matches:
            char_range = set(range(m["start"], m["end"]))
            matched_char_positions.update(char_range)
            if m["match_type"] == "exact":
                exact_char_positions.update(char_range)
            else:
                paraphrase_char_positions.update(char_range)

        text_length = max(1, len(analysis_text))
        overall_similarity = min(100.0, round((len(matched_char_positions) / text_length) * 100, 1))
        exact_similarity = min(100.0, round((len(exact_char_positions) / text_length) * 100, 1))
        paraphrase_similarity = min(100.0, round((len(paraphrase_char_positions) / text_length) * 100, 1))

        # Source breakdown calculation
        source_breakdown = []
        for src_title, char_set in source_matched_words.items():
            pct = min(100.0, round((len(char_set) / text_length) * 100, 1))
            if pct > 0.0:
                source_breakdown.append({
                    "source_title": src_title,
                    "percentage": pct
                })

        source_breakdown.sort(key=lambda s: s["percentage"], reverse=True)

        # Merge contiguous or overlapping matches for clean UI rendering
        all_matches.sort(key=lambda x: x["start"])

        return {
            "overall_similarity": overall_similarity,
            "exact_similarity": exact_similarity,
            "paraphrase_similarity": paraphrase_similarity,
            "total_words": total_words,
            "matched_characters": len(matched_char_positions),
            "matched_spans": all_matches,
            "source_breakdown": source_breakdown,
            "quotes_found": len(quotes),
            "bibliography_excluded": cleaned["bibliography_meta"]["has_bibliography"] if exclude_bibliography else False,
            "clean_metadata": {
                "quotes_count": len(quotes),
                "has_bibliography": cleaned["bibliography_meta"]["has_bibliography"],
                "bibliography_heading": cleaned["bibliography_meta"]["heading"]
            }
        }
