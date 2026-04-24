from app.services.email_analyzer import analyze_email
from app.utils.url_extractor import extract_urls


def test_extract_urls_includes_bare_domains_and_email_domains():
    text = """
    Sender: alerts@paypa1-support.com
    Visit secure-paypa1-support.com/verify or www.safe-site.org now.
    """

    urls = extract_urls(text)

    assert "paypa1-support.com" in urls
    assert "secure-paypa1-support.com" in urls
    assert "www.safe-site.org" in urls


def test_analyze_email_passes_subject_and_sender_into_url_scan(monkeypatch):
    captured = {}

    def fake_get_bert_score(_text):
        return {"bert_score": 0.2, "confidence": 0.8, "label": "low_risk"}

    def fake_analyze_urls(text):
        captured["text"] = text
        return {
            "urls": [],
            "max_url_score": 0.0,
            "avg_url_score": 0.0,
            "url_reasons": [],
        }

    monkeypatch.setattr("app.services.email_analyzer.get_bert_score", fake_get_bert_score)
    monkeypatch.setattr("app.services.email_analyzer.analyze_urls", fake_analyze_urls)

    result = analyze_email(
        subject="verify account at secure-paypa1-support.com",
        sender="alerts@paypa1-support.com",
        body_text="plain body",
        html_text="",
        ocr_image_text="",
    )

    assert "secure-paypa1-support.com" in captured["text"]
    assert "alerts@paypa1-support.com" in captured["text"]
    assert result["url_score"] == 0.0
