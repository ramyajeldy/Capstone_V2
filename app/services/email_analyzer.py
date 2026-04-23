from app.services.bert_service import get_bert_score
from app.services.url_intelligence_service import analyze_urls
from app.services.html_parser import get_html_score, get_html_signals
from app.services.risk_engine import calculate_risk_score
from app.utils.text_cleaner import build_combined_email_text


def analyze_email(
    subject: str = "",
    sender: str = "",
    body_text: str = "",
    html_text: str = "",
    ocr_image_text: str = "",
    attachments: list | None = None
) -> dict:
    attachments = attachments or []
    ocr_text = ocr_image_text or ""

    combined_text = build_combined_email_text(
        subject=subject,
        sender=sender,
        body_text=body_text,
        html_text=html_text,
        ocr_text=ocr_text
    )

    bert_result = get_bert_score(combined_text)
    print("\n========== EMAIL ANALYZER DEBUG ==========")
    print("COMBINED TEXT:", combined_text[:300])
    print("BERT RESULT:", bert_result)

    url_result = analyze_urls("\n".join([body_text, html_text, ocr_text]))

    html_input = html_text if html_text.strip() else (body_text if "<" in body_text else "")
    html_score = get_html_score(html_input)
    html_signals = get_html_signals(html_input)

    final_score = calculate_risk_score(
        bert_score=bert_result["bert_score"],
        url_score=url_result["max_url_score"],
        domain_score=0.0,
        html_score=html_score,
    )

    if final_score >= 0.7:
        label = "high_risk"
    elif final_score >= 0.4:
        label = "medium_risk"
    else:
        label = "low_risk"

    if url_result["max_url_score"] >= 0.6:
        label = "high_risk"
        final_score = max(final_score, 0.75)
    elif url_result["max_url_score"] >= 0.4:
        label = "medium_risk"
        final_score = max(final_score, 0.5)

    if bert_result["bert_score"] >= 0.5:
        label = "high_risk"
        final_score = max(final_score, 0.7)
    elif bert_result["bert_score"] >= 0.35:
        if label == "low_risk":
            label = "medium_risk"
        final_score = max(final_score, 0.45)

    if html_score >= 0.5:
        label = "high_risk"
        final_score = max(final_score, 0.7)

    return {
        "risk_score": round(final_score, 4),
        "confidence": bert_result["confidence"],
        "label": label,
        "bert_score": bert_result["bert_score"],
        "url_score": url_result["max_url_score"],
        "html_score": html_score,
        "html_signals": html_signals,
        "url_reasons": url_result["url_reasons"],
        "urls": url_result["urls"],
        "ocr_text": ocr_text,
    }