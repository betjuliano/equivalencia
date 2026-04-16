import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from backend.src.infrastructure.pdf_extractor import extract_metadata_from_text
import pdfplumber

def verify_extraction(path):
    print(f"\n--- Verifying {os.path.basename(path)} ---")
    with pdfplumber.open(path) as pdf:
        text = "\n".join(p.extract_text() for p in pdf.pages if p.extract_text())
        meta = extract_metadata_from_text(text)
        print(f"Extracted: {meta}")

if __name__ == "__main__":
    verify_extraction(r"c:\Users\pccli\Documents\EQUIVALENCIA\conteudo_programatico_DPADP0210.pdf")
    verify_extraction(r"c:\Users\pccli\Documents\EQUIVALENCIA\conteudo_programatico_JUR1120.pdf")
