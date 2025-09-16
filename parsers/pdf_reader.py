# parsers/pdf_reader.py
try:
    from pypdf import PdfReader          
except ImportError:                      
    from PyPDF2 import PdfReader

def read_pdf_bytes(b: bytes, max_pages: int = 50) -> str:
    reader = PdfReader(b)
    pages = min(len(reader.pages), max_pages)
    parts = []
    for i in range(pages):
        txt = reader.pages[i].extract_text() or ""
        parts.append(txt)
    return "\n".join(parts).strip()
