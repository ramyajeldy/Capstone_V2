from app.services.bert_service import get_bert_score
from app.services.url_intelligence_service import analyze_urls
from app.services.html_parser import get_html_score
from app.services.risk_engine import calculate_risk_score


def analyze_email(subject: str = "", body_text: str = "", html_text: str = ""):

    text = subject + " " + body_text + " " + html_text

    # BERT
    bert_score = get_bert_score(text)

    # URL
    url_result = analyze_urls(text)
    url_score = url_result["max_url_score"]

    # HTML
    html_score = get_html_score(html_text)

    # FINAL SCORE
    final_score = calculate_risk_score(
        bert_score,
        url_score,
        0.0,  # no domain_age in her project
        html_score
    )

    # LABEL
    if final_score > 0.7:
        label = "high_risk"
    elif final_score > 0.4:
        label = "medium_risk"
    else:
        label = "low_risk"

    return {
        "risk_score": final_score,
        "label": label,
        "bert_score": bert_score,
        "url_score": url_score,
        "html_score": html_score
    }