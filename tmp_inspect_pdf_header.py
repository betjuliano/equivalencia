import pdfplumber
from pathlib import Path

def inspect_pdf_header(path):
    p = Path(path)
    with pdfplumber.open(str(p)) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text()
        lines = text.split("\n")
        print("--- TOP 40 LINES OF PAGE 1 ---")
        for i, line in enumerate(lines[:40]):
            print(f"{i+1:02}: {line}")

if __name__ == "__main__":
    inspect_pdf_header(r"c:\Users\pccli\Documents\EQUIVALENCIA\conteudo_programatico_DPADP0210.pdf")
