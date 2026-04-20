import re

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+", " url ", text)
    text = re.sub(r"\d+", " ", text)
    text = re.sub(r"[^a-z\s<>:/.@_-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def build_combined_email_text(
    subject: str = "",
    sender: str = "",
    body_text: str = "",
    html_text: str = "",
    ocr_text: str = ""
) -> str:
    raw_text = f"""
    SUBJECT:
    {subject}

    SENDER:
    {sender}

    OCR_EXTRACTED_TEXT:
    {ocr_text}

    BODY_TEXT:
    {body_text}

    HTML_TEXT:
    {html_text}
    """
    return clean_text(raw_text)