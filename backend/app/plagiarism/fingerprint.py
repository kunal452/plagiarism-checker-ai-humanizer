import re
import hashlib
from typing import List, Set, Dict, Tuple, Any

class FingerprintEngine:
    """
    Implements Exact & Near-Exact Plagiarism Detection:
    - 5 to 7-word n-gram shingles (Turnitin standard)
    - MinHash and Locality-Sensitive Hashing (LSH)
    - Rabin-Karp rolling hash for fast substring matching
    """

    NUM_PERMUTATIONS = 64
    PRIME = (1 << 31) - 1

    # Deterministic hash seeds for MinHash
    HASH_SEEDS = [
        (1301081 * i + 3571) % 1000003 for i in range(NUM_PERMUTATIONS)
    ]

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """
        Tokenizes text into cleaned lowercase words.
        """
        return re.findall(r'[a-zA-Z0-9]+', text.lower())

    @classmethod
    def generate_shingles(cls, text: str, k: int = 5) -> List[Tuple[str, int, int]]:
        """
        Generates k-word shingles along with character start and end offsets in the original text.
        Returns list of (shingle_string, start_char, end_char).
        """
        matches = list(re.finditer(r'[a-zA-Z0-9]+', text.lower()))
        if len(matches) < k:
            return []

        shingles = []
        for i in range(len(matches) - k + 1):
            window = matches[i : i + k]
            shingle_str = " ".join(m.group() for m in window)
            start_pos = window[0].start()
            end_pos = window[-1].end()
            shingles.append((shingle_str, start_pos, end_pos))

        return shingles

    @classmethod
    def compute_minhash(cls, shingles: List[str]) -> List[int]:
        """
        Computes MinHash signature vector for a set of shingles.
        """
        if not shingles:
            return [0] * cls.NUM_PERMUTATIONS

        # Hash each shingle to an integer
        shingle_hashes = []
        for s in shingles:
            h = int(hashlib.md5(s.encode('utf-8')).hexdigest()[:8], 16)
            shingle_hashes.append(h)

        signature = []
        for seed in cls.HASH_SEEDS:
            min_val = float('inf')
            for h in shingle_hashes:
                permuted = (h ^ seed) % cls.PRIME
                if permuted < min_val:
                    min_val = permuted
            signature.append(int(min_val))

        return signature

    @classmethod
    def estimate_jaccard(cls, sig1: List[int], sig2: List[int]) -> float:
        """
        Estimates Jaccard similarity between two MinHash signatures.
        """
        if not sig1 or not sig2 or len(sig1) != len(sig2):
            return 0.0
        matches = sum(1 for a, b in zip(sig1, sig2) if a == b)
        return round(matches / len(sig1), 4)

    @classmethod
    def rabin_karp_fingerprint(cls, s: str, base: int = 256, mod: int = 1000000007) -> int:
        """
        Rabin-Karp polynomial rolling hash of a string.
        """
        h = 0
        for char in s:
            h = (h * base + ord(char)) % mod
        return h

    @classmethod
    def find_exact_matching_spans(cls, query_text: str, source_text: str, k: int = 6) -> List[Dict[str, Any]]:
        """
        Locates exact matched spans between query document and a reference source.
        Merges adjacent overlapping matches into continuous spans.
        """
        query_shingles = cls.generate_shingles(query_text, k=k)
        source_shingles = cls.generate_shingles(source_text, k=k)

        source_dict: Dict[str, List[Tuple[int, int]]] = {}
        for s_str, s_start, s_end in source_shingles:
            source_dict.setdefault(s_str, []).append((s_start, s_end))

        matched_intervals = []
        for q_str, q_start, q_end in query_shingles:
            if q_str in source_dict:
                for s_start, s_end in source_dict[q_str]:
                    matched_intervals.append({
                        "query_start": q_start,
                        "query_end": q_end,
                        "source_start": s_start,
                        "source_end": s_end,
                        "text": query_text[q_start:q_end]
                    })

        # Merge overlapping intervals in query text
        if not matched_intervals:
            return []

        matched_intervals.sort(key=lambda x: x["query_start"])
        merged = []
        current = matched_intervals[0].copy()

        for next_item in matched_intervals[1:]:
            if next_item["query_start"] <= current["query_end"]:
                # Overlap or contiguous
                current["query_end"] = max(current["query_end"], next_item["query_end"])
                current["source_end"] = max(current["source_end"], next_item["source_end"])
                current["text"] = query_text[current["query_start"] : current["query_end"]]
            else:
                merged.append(current)
                current = next_item.copy()

        merged.append(current)
        return merged
