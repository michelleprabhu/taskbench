import io
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes

def run_ocr_on_image_bytes(b: bytes, lang: str = "eng") -> str:
    try:
        img = Image.open(io.BytesIO(b))
        text = pytesseract.image_to_string(img, lang=lang)
        return text.strip()
    except Exception as e:
        return f"[OCR failed: {e}]"

def run_ocr_on_pdf(b: bytes, lang: str = "eng", max_pages: int = 10) -> str:
    try:
        pages = convert_from_bytes(b, dpi=200, first_page=1, last_page=max_pages)
        parts = []
        for i, page in enumerate(pages):
            text = pytesseract.image_to_string(page, lang=lang)
            if text.strip():
                parts.append(f"[Page {i+1} OCR]\n{text.strip()}")
        return "\n\n".join(parts).strip()
    except Exception as e:
        return f"[PDF OCR failed: {e}]"
