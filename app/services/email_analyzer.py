import logging

from app.services.bert_service import get_bert_score
from app.services.url_intelligence_service import analyze_urls
from app.services.html_parser import get_html_score, get_html_signals
from app.services.risk_engine import calculate_risk_score
from app.utils.text_cleaner import build_combined_email_text

logger = logging.getLogger(__name__)


def analyze_email(
    subject: str = "",
    sender: str = "",
    body_text: str = "",
    html_text: str = "",
    ocr_image_text: str = "",
    attachments: list | None = None,
) -> dict:
    attachments = attachments or []

    logger.info(
        "analyze_email called | subject_len=%s | sender_len=%s | body_len=%s | html_len=%s | ocr_len=%s | attachments=%s",
        len(subject or ""),
        len(sender or ""),
        len(body_text or ""),
        len(html_text or ""),
        len(ocr_image_text or ""),
        len(attachments),
    )

    # Use OCR text already passed from main.py
    ocr_text = (ocr_image_text or "").strip()

    # Combine text for BERT
    try:
        combined_text = build_combined_email_text(
            subject=subject,
            sender=sender,
            body_text=body_text,
            html_text=html_text,
            ocr_text=ocr_text,
        )
    except TypeError:
        # fallback if utility signature differs
        combined_text = " ".join(
            filter(
                None,
                [subject, sender, body_text, html_text, ocr_text],
            )
        )

    combined_text = combined_text.replace("\n", " ").strip()
    combined_text = combined_text[:2000]

    logger.info("combined_text_length=%s", len(combined_text))

    # BERT
    bert_result = get_bert_score(combined_text)

    # URL
    url_scan_text = "\n".join(
        filter(
            None,
            [
                subject,
                sender,
                body_text,
                html_text,
                ocr_text,
            ],
        )
    )
    url_result = analyze_urls(url_scan_text)
    extracted_urls = url_result["urls"]
    extracted_url_values = []
    for item in extracted_urls:
        if isinstance(item, dict):
            extracted_url_values.append(item.get("url") or item.get("normalized_url") or "")
        else:
            extracted_url_values.append(str(item))

    # HTML
    html_score = get_html_score(html_text)
    html_signals = get_html_signals(html_text)

    # Risk score
    final_score = calculate_risk_score(
        bert_score=bert_result["bert_score"],
        url_score=url_result["max_url_score"],
        domain_score=0.0,
        html_score=html_score,
    )

    # Label
    if final_score >= 0.7:
        label = "high_risk"
    elif final_score >= 0.4:
        label = "medium_risk"
    else:
        label = "low_risk"

    # Overrides
    if url_result["max_url_score"] >= 0.6:
        label = "high_risk"
        final_score = max(final_score, 0.75)

    elif url_result["max_url_score"] >= 0.4:
        label = "medium_risk"
        final_score = max(final_score, 0.5)

    if bert_result["bert_score"] >= 0.8:
        label = "high_risk"
        final_score = max(final_score, 0.8)

    if html_score >= 0.5:
        label = "high_risk"
        final_score = max(final_score, 0.7)

    result = {
        "risk_score": round(final_score, 4),
        "confidence": bert_result["confidence"],
        "label": label,
        "bert_score": bert_result["bert_score"],
        "url_score": url_result["max_url_score"],
        "html_score": html_score,
        "html_signals": html_signals,
        "url_reasons": url_result["url_reasons"],
        "urls": extracted_urls,
        "debug": {
            "subject_length": len(subject or ""),
            "sender_length": len(sender or ""),
            "body_text_length": len(body_text or ""),
            "html_text_length": len(html_text or ""),
            "ocr_text_length": len(ocr_text),
            "combined_text_length": len(combined_text),
            "combined_text_preview": combined_text[:300],
            "url_scan_text_length": len(url_scan_text),
            "extracted_url_count": len(extracted_url_values),
            "extracted_urls": extracted_url_values[:10],
            "html_signal_count": len(html_signals),
        },
    }

    logger.info(
        "analyze_email completed | label=%s | risk_score=%s | bert_score=%s | url_score=%s | html_score=%s",
        result["label"],
        result["risk_score"],
        result["bert_score"],
        result["url_score"],
        result["html_score"],
    )

    return result
