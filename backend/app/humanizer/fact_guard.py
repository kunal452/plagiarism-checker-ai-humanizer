import re
from typing import Dict, List, Set, Tuple

class FactGuard:
    """
    Prevents semantic drift during text humanization:
    - Extracts numbers, statistics, percentages, years, dates
    - Extracts academic citations (e.g. [1], [1, 2], (Smith et al., 2023))
    - Validates that rewritten text does not corrupt or omit factual tokens
    """

    # Citation patterns
    CITATION_PATTERNS = [
        re.compile(r'\[\s*\d+(?:\s*[,-]\s*\d+)*\s*\]'),                  # [1], [1, 2], [1-3]
        re.compile(r'\([A-Z][a-zA-Z]+(?:\s+et\s+al\.?)?,\s*\d{4}[a-z]?\)'), # (Johnson et al., 2023)
        re.compile(r'\b[A-Z][a-zA-Z]+\s+et\s+al\.\s*\(\d{4}\)'),           # Johnson et al. (2023)
    ]

    # Numeric and factual patterns
    NUMBER_PATTERNS = [
        re.compile(r'\b\d+(?:\.\d+)?%'),                                   # percentages: 18.4%, 95%
        re.compile(r'\$\s*\d+(?:,\d{3})*(?:\.\d+)?'),                      # currency: $500, $1.2M
        re.compile(r'\b\d{4}\b'),                                           # years: 2024, 1998
        re.compile(r'\b\d+(?:\.\d+)?\s*(?:mg|kg|ml|gb|tb|mb|ghz|ms|s|km|m)\b', re.IGNORECASE), # units
        re.compile(r'\b\d+(?:\.\d+)?\b'),                                  # standalone numbers
    ]

    @classmethod
    def extract_facts(cls, text: str) -> Dict[str, Set[str]]:
        citations = set()
        for pat in cls.CITATION_PATTERNS:
            for match in pat.finditer(text):
                citations.add(match.group().strip())

        numbers = set()
        for pat in cls.NUMBER_PATTERNS:
            for match in pat.finditer(text):
                val = match.group().strip()
                if val not in citations:
                    numbers.add(val)

        return {
            "citations": citations,
            "numbers": numbers
        }

    @classmethod
    def audit_fidelity(cls, original_text: str, humanized_text: str) -> Dict[str, Any]:
        """
        Compares factual tokens in original vs humanized text to ensure zero semantic drift.
        """
        orig_facts = cls.extract_facts(original_text)
        new_facts = cls.extract_facts(humanized_text)

        missing_citations = orig_facts["citations"] - new_facts["citations"]
        missing_numbers = orig_facts["numbers"] - new_facts["numbers"]

        is_faithful = len(missing_citations) == 0 and len(missing_numbers) == 0
        fidelity_score = 100.0

        total_critical_items = len(orig_facts["citations"]) + len(orig_facts["numbers"])
        if total_critical_items > 0:
            lost_items = len(missing_citations) + len(missing_numbers)
            fidelity_score = round(max(0.0, (1 - (lost_items / total_critical_items)) * 100), 1)

        return {
            "is_faithful": is_faithful,
            "fidelity_score": fidelity_score,
            "missing_citations": list(missing_citations),
            "missing_numbers": list(missing_numbers),
            "total_facts_tracked": total_critical_items
        }

    @classmethod
    def restore_missing_citations(cls, original_text: str, humanized_text: str) -> str:
        """
        If critical citations were dropped, appends a bibliography/attribution safeguard.
        """
        audit = cls.audit_fidelity(original_text, humanized_text)
        if audit["missing_citations"]:
            recovered = " " + " ".join(audit["missing_citations"])
            return humanized_text.rstrip() + recovered
        return humanized_text
