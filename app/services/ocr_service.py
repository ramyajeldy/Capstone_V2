import os
import shutil
import io
import logging
from PIL import Image
import pytesseract

logger = logging.getLogger(__name__)


def _resolve_tesseract_cmd() -> str | None:
    configured_path = os.getenv("TESSERACT_CMD", "").strip()
    if configured_path:
        return configured_path

    discovered_path = shutil.which("tesseract")
    if discovered_path:
        return discovered_path

    if os.name == "nt":
        windows_candidates = (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        )
        for candidate in windows_candidates:
            if os.path.exists(candidate):
                return candidate

    return None


_tesseract_cmd = _resolve_tesseract_cmd()
if _tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = _tesseract_cmd
    logger.info("Using Tesseract executable: %s", _tesseract_cmd)
else:
    logger.warning("Tesseract executable was not found. OCR requests will fail until it is installed.")


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
        content_type = (att.get("content_type") or "").lower()
        image_bytes = att.get("data") or b""
        if not image_bytes:
            continue

        if content_type.startswith("image/") or filename.endswith((".png", ".jpg", ".jpeg", ".webp")):
            text = extract_text_from_image_bytes(image_bytes)
            if text:
                texts.append(text)

    return "\n".join(texts).strip()
