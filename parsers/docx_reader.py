from docx import Document
import io

def read_docx_bytes(b: bytes) -> str:
    f = io.BytesIO(b)
    doc = Document(f)
    texts = []
    for p in doc.paragraphs:
        texts.append(p.text)
    return "\n".join(texts).strip()
