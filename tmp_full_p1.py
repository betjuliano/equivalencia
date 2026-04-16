import pdfplumber
from pathlib import Path

def inspect_pdf_absolute_start(path):
    p = Path(path)
    with pdfplumber.open(str(p)) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text()
        print("--- COMPLETE FIRST PAGE TEXT ---")
        print(text)
        print("--- END OF FIRST PAGE ---")

if __name__ == "__main__":
    inspect_pdf_absolute_start(r"c:\Users\pccli\Documents\EQUIVALENCIA\conteudo_programatico_DPADP0210.pdf")
