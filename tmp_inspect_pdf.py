import pdfplumber
import sys
from pathlib import Path

def inspect_pdf(path):
    p = Path(path)
    if not p.exists():
        print(f"File {path} not found")
        return

    print(f"--- Inspecting {p.name} ---")
    with pdfplumber.open(str(p)) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            print(f"--- Page {i+1} ---")
            print(text)
            print("-" * 20)

if __name__ == "__main__":
    inspect_pdf(r"c:\Users\pccli\Documents\EQUIVALENCIA\conteudo_programatico_DPADP0210.pdf")
