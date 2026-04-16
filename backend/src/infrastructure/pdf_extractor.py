"""Infrastructure — PDF text extractor (Spec.md section 9.7)"""
from __future__ import annotations
from pathlib import Path
from typing import Optional


import pdfplumber
import re
from pathlib import Path
from typing import Optional, Dict, Any


async def extract_text_from_pdf(pdf_path: Path) -> Optional[str]:
    """Extract text from a PDF file. Returns None if extraction fails."""
    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            pages_text = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
            return "\n".join(pages_text) if pages_text else None
    except Exception:
        return None


def extract_metadata_from_text(text: str) -> Dict[str, Any]:
    """Extract Code, Name, Institution and Workload from UFSM-style text."""
    if not text:
        return {}
        
    lines = text.split("\n")
    metadata: Dict[str, Any] = {
        "codigo": None,
        "nome": None,
        "instituicao": "UFSM" if lines and "UFSM" in lines[0] else None,
        "ch": None,
    }
    
    # Patterns based on UFSM layout
    code_match = re.search(r"C[óo]digo:\s*([A-Z0-9]+)", text)
    if code_match:
        metadata["codigo"] = code_match.group(1)
        
    name_match = re.search(r"Nome:\s*(.+)", text)
    if name_match:
        metadata["nome"] = name_match.group(1).strip()
        
    ch_match = re.search(r"Carga\s+Hor[áa]ria\s*(\d+)", text, re.IGNORECASE)
    if ch_match:
        metadata["ch"] = float(ch_match.group(1))
        
    if not metadata["instituicao"] and "UNIVERSIDADE FEDERAL DE SANTA MARIA" in text:
        metadata["instituicao"] = "UFSM"
        
    return metadata
