import base64
from .pdf_reader import read_pdf_bytes
from .docx_reader import read_docx_bytes
from .md_txt_reader import read_md_or_txt_bytes
from .html_reader import read_html_bytes
from .ocr_reader import run_ocr_on_image_bytes, run_ocr_on_pdf

def extract_text(filename: str, file_bytes: bytes,
                 enable_html=True, max_pages=50,
                 enable_ocr=False, ocr_lang="eng") -> str:
    name = (filename or "").lower()
    text = ""

    if name.endswith(".pdf"):
        text = read_pdf_bytes(file_bytes, max_pages)
        if enable_ocr and (not text or len(text) < 20):
            return run_ocr_on_pdf(file_bytes, lang=ocr_lang, max_pages=min(max_pages,10))
        return text

    if name.endswith(".docx"):
        return read_docx_bytes(file_bytes)

    if name.endswith(".md") or name.endswith(".txt"):
        return read_md_or_txt_bytes(file_bytes)

    if enable_html and (name.endswith(".html") or name.endswith(".htm")):
        return read_html_bytes(file_bytes)

    if enable_ocr and name.endswith((".png",".jpg",".jpeg",".tiff",".bmp")):
        return run_ocr_on_image_bytes(file_bytes, lang=ocr_lang)

    try:
        return file_bytes.decode("utf-8", errors="ignore")
    except:
        return ""

def decode_base64(data: str) -> bytes:
    return base64.b64decode(data.split(",")[-1].encode())

