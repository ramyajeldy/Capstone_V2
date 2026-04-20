from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

import io  

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