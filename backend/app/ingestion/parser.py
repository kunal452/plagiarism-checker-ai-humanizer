import io
import os
from typing import Dict, Any, List, Optional
import pymupdf  # PyMuPDF
import docx      # python-docx

class DocumentParser:
    """
    Extracts text from PDF, DOCX, and raw text while preserving paragraph structure
    and capturing page/layout metadata.
    """

    @staticmethod
    def parse_pdf(file_bytes: bytes, filename: str = "document.pdf") -> Dict[str, Any]:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
        pages_content = []
        full_text_parts = []
        char_count = 0

        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_text = page.get_text("text")
            # Extract text blocks with layout coordinates if available
            blocks = page.get_text("blocks")
            cleaned_blocks = []
            for b in blocks:
                # b format: (x0, y0, x1, y1, text, block_no, block_type)
                if len(b) >= 5 and b[4].strip():
                    cleaned_blocks.append({
                        "bbox": [round(coord, 2) for coord in b[:4]],
                        "text": b[4].strip()
                    })

            start_char = char_count
            full_text_parts.append(page_text)
            char_count += len(page_text) + 1

            pages_content.append({
                "page_number": page_idx + 1,
                "text": page_text,
                "start_char": start_char,
                "end_char": char_count,
                "blocks": cleaned_blocks
            })

        full_text = "\n".join(full_text_parts)
        return {
            "filename": filename,
            "format": "pdf",
            "page_count": len(doc),
            "text": full_text,
            "pages": pages_content
        }

    @staticmethod
    def parse_docx(file_bytes: bytes, filename: str = "document.docx") -> Dict[str, Any]:
        file_stream = io.BytesIO(file_bytes)
        doc = docx.Document(file_stream)
        paragraphs = []
        full_text_parts = []
        char_count = 0

        for idx, para in enumerate(doc.paragraphs):
            text = para.text.strip()
            if not text:
                continue
            start_char = char_count
            full_text_parts.append(text)
            char_count += len(text) + 2  # account for \n\n
            paragraphs.append({
                "paragraph_index": idx,
                "text": text,
                "style": para.style.name if para.style else "Normal",
                "start_char": start_char,
                "end_char": char_count
            })

        full_text = "\n\n".join(full_text_parts)
        return {
            "filename": filename,
            "format": "docx",
            "page_count": max(1, len(paragraphs) // 4),
            "text": full_text,
            "paragraphs": paragraphs
        }

    @staticmethod
    def parse_text(text: str, filename: str = "document.txt") -> Dict[str, Any]:
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        return {
            "filename": filename,
            "format": "txt",
            "page_count": max(1, len(text) // 2000),
            "text": text,
            "paragraphs": [{"paragraph_index": i, "text": p} for i, p in enumerate(paragraphs)]
        }

    @classmethod
    def parse_file(cls, filename: str, content: bytes) -> Dict[str, Any]:
        lower_name = filename.lower()
        if lower_name.endswith(".pdf"):
            return cls.parse_pdf(content, filename)
        elif lower_name.endswith(".docx") or lower_name.endswith(".doc"):
            return cls.parse_docx(content, filename)
        else:
            try:
                decoded = content.decode("utf-8")
            except UnicodeDecodeError:
                decoded = content.decode("latin-1", errors="ignore")
            return cls.parse_text(decoded, filename)
