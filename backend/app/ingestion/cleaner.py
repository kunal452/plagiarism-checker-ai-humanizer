import re
from typing import Dict, Any, List, Tuple

class DocumentCleaner:
    """
    Cleans raw document text, strips running headers/footers, and detects
    bibliography sections and quotation blocks to eliminate false positives in plagiarism detection.
    """

    # Headers/footers patterns (e.g. "Page 1 of 5", "Confidential", etc.)
    PAGE_NUMBER_PATTERNS = [
        re.compile(r'^\s*(?:page|pg\.?)\s*\d+(?:\s*(?:of|\/)\s*\d+)?\s*$', re.IGNORECASE),
        re.compile(r'^\s*\d+\s*(?:of|\/)\s*\d+\s*$', re.IGNORECASE),
        re.compile(r'^\s*-\s*\d+\s*-\s*$', re.IGNORECASE),
        re.compile(r'^\s*\d+\s*$', re.IGNORECASE),
    ]

    # Bibliography headings
    BIBLIOGRAPHY_HEADINGS = [
        re.compile(r'^\s*(?:references|bibliography|works\s+cited|sources|literature\s+cited|citations)\s*[:.]?\s*$', re.IGNORECASE | re.MULTILINE),
        re.compile(r'\n\s*(?:references|bibliography|works\s+cited|sources)\s*[:.]?\s*\n', re.IGNORECASE),
    ]

    # Quotation patterns (straight quotes, curly quotes, guillemets)
    QUOTE_PATTERNS = [
        re.compile(r'("[^"]{15,}")', re.DOTALL),
        re.compile(r'(“[^”]{15,}”)', re.DOTALL),
        re.compile(r'(‘[^’]{15,}’)', re.DOTALL),
        re.compile(r'<<([^>]{15,})>>', re.DOTALL),
    ]

    @classmethod
    def strip_headers_and_footers(cls, text: str) -> str:
        lines = text.split("\n")
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            # Check if this line is purely a page number or footer noise
            is_noise = any(pattern.match(stripped) for pattern in cls.PAGE_NUMBER_PATTERNS)
            if not is_noise:
                cleaned_lines.append(line)
        return "\n".join(cleaned_lines)

    @classmethod
    def identify_bibliography(cls, text: str) -> Tuple[str, str, Dict[str, Any]]:
        """
        Splits text into (body_text, bibliography_text) if a bibliography section exists.
        Returns detailed span info.
        """
        earliest_split_pos = -1
        heading_match_str = ""

        for pattern in cls.BIBLIOGRAPHY_HEADINGS:
            for match in pattern.finditer(text):
                # Ensure the heading is in the latter half of the document to avoid false triggers
                pos = match.start()
                if pos > len(text) * 0.35 and (earliest_split_pos == -1 or pos < earliest_split_pos):
                    earliest_split_pos = pos
                    heading_match_str = match.group().strip()

        if earliest_split_pos != -1:
            body = text[:earliest_split_pos].rstrip()
            bibliography = text[earliest_split_pos:].lstrip()
            return body, bibliography, {
                "has_bibliography": True,
                "heading": heading_match_str,
                "start_char": earliest_split_pos,
                "end_char": len(text),
                "length": len(bibliography)
            }
        
        return text, "", {
            "has_bibliography": False,
            "heading": "",
            "start_char": -1,
            "end_char": -1,
            "length": 0
        }

    @classmethod
    def extract_quotations(cls, text: str) -> List[Dict[str, Any]]:
        """
        Finds all quoted passages with start and end character offsets.
        """
        quotations = []
        for pattern in cls.QUOTE_PATTERNS:
            for match in pattern.finditer(text):
                quote_text = match.group()
                start = match.start()
                end = match.end()
                # Check for overlap with already found quotes
                if not any(q["start"] <= start < q["end"] or q["start"] < end <= q["end"] for q in quotations):
                    quotations.append({
                        "text": quote_text,
                        "start": start,
                        "end": end,
                        "length": len(quote_text)
                    })

        quotations.sort(key=lambda q: q["start"])
        return quotations

    @classmethod
    def clean_document(cls, raw_text: str) -> Dict[str, Any]:
        """
        Full cleaning pipeline:
        1. Strips header/footer noise.
        2. Segregates bibliography section.
        3. Identifies and marks quotes.
        """
        stripped_text = cls.strip_headers_and_footers(raw_text)
        body_text, bib_text, bib_meta = cls.identify_bibliography(stripped_text)
        quotes = cls.extract_quotations(body_text)

        return {
            "full_text": stripped_text,
            "body_text": body_text,
            "bibliography_text": bib_text,
            "bibliography_meta": bib_meta,
            "quotations": quotes,
            "total_chars": len(stripped_text),
            "body_chars": len(body_text)
        }
