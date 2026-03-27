"""Infrastructure — PDF text extractor (Spec.md section 9.7)"""
from __future__ import annotations
from pathlib import Path
from typing import Optional


async def extract_text_from_pdf(pdf_path: Path) -> Optional[str]:
    """Extract text from a PDF file. Returns None if extraction fails."""
    try:
        import pdfplumber
        with pdfplumber.open(str(pdf_path)) as pdf:
            pages_text = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
            return "\n".join(pages_text) if pages_text else None
    except Exception as e:
        return None
