import io
import docx
import pymupdf
from typing import Dict, Any

class DocumentExporter:
    """
    Exports clean humanized text or detailed plagiarism reports as DOCX, PDF, or TXT.
    """

    @staticmethod
    def export_to_docx(text: str, title: str = "Humanized Document") -> bytes:
        doc = docx.Document()
        doc.add_heading(title, level=0)
        
        paragraphs = text.split("\n\n")
        for p in paragraphs:
            clean_p = p.strip()
            if clean_p:
                doc.add_paragraph(clean_p)

        file_stream = io.BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream.getvalue()

    @staticmethod
    def export_to_pdf(text: str, title: str = "Humanized Document") -> bytes:
        # Create a clean PDF using PyMuPDF
        doc = pymupdf.open()
        page = doc.new_page()
        
        # Insert title
        rect_title = pymupdf.Rect(50, 50, 550, 80)
        page.insert_textbox(rect_title, title, fontsize=18, fontname="helv", color=(0.1, 0.2, 0.4))
        
        # Split text into pages and insert textboxes
        paragraphs = text.split("\n\n")
        y = 95
        line_height = 14
        
        for p in paragraphs:
            clean_p = p.strip()
            if not clean_p:
                continue
            
            # Estimate height needed
            words = clean_p.split()
            estimated_lines = max(1, len(words) // 12)
            block_height = estimated_lines * line_height + 12
            
            if y + block_height > 780:
                page = doc.new_page()
                y = 50
                
            rect = pymupdf.Rect(50, y, 550, y + block_height + 20)
            page.insert_textbox(rect, clean_p, fontsize=10, fontname="helv", color=(0.15, 0.15, 0.15))
            y += block_height + 8

        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes
