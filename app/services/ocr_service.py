import os
import shutil
from PIL import Image
import pytesseract

import io  

_WINDOWS_TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if os.name == "nt" and os.path.exists(_WINDOWS_TESSERACT):
    pytesseract.pytesseract.tesseract_cmd = _WINDOWS_TESSERACT
elif shutil.which("tesseract"):
    pytesseract.pytesseract.tesseract_cmd = shutil.which("tesseract")

def extract_text_from_image_bytes(image_bytes: bytes) -> str:
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        print("OCR Error:", e)
        return ""


def extract_ocr_from_attachments(attachments: list) -> str:
    texts = []

    for att in attachments:
        filename = (att.get("filename") or "").lower()
        content_type = att.get("content_type", "")
        data = att.get("data")

        if not data:
            continue

        if content_type.startswith("image/") or filename.endswith((".png", ".jpg", ".jpeg")):
            text = extract_text_from_image_bytes(data)
            if text:
                texts.append(text)

    return "\n".join(texts).strip()
