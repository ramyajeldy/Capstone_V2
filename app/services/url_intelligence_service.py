from app.utils.url_extractor import extract_urls

SUSPICIOUS_KEYWORDS = [
    "login", "verify", "secure", "account", "reset",
    "password", "update", "confirm", "wallet", "invoice", "pay"
]

SHORTENERS = ["bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd"]

SUSPICIOUS_TLDS = [".xyz", ".top", ".click", ".buzz", ".info"]

def score_single_url(url: str) -> dict:
    score = 0.0
    reasons = []

    lower_url = url.lower()

    if any(shortener in lower_url for shortener in SHORTENERS):
        score += 0.30
        reasons.append("URL shortener used")

    if "@" in url:
        score += 0.20
        reasons.append("@ symbol found in URL")

    if len(url) > 75:
        score += 0.15
        reasons.append("Unusually long URL")

    if sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in lower_url) >= 2:
        score += 0.20
        reasons.append("Multiple suspicious keywords in URL")

    if any(tld in lower_url for tld in SUSPICIOUS_TLDS):
        score += 0.20
        reasons.append("Suspicious top-level domain")

    if lower_url.count("-") >= 2:
        score += 0.10
        reasons.append("Multiple hyphens in URL")

    return {
        "url": url,
        "final_probability": round(min(score, 1.0), 4),
        "prediction": "phishing" if score >= 0.5 else "benign",
        "reasons": reasons if reasons else ["No major URL red flags detected"]
    }

def analyze_urls(text: str) -> dict:
    urls = extract_urls(text)

    if not urls:
        return {
            "urls": [],
            "max_url_score": 0.0,
            "avg_url_score": 0.0,
            "url_reasons": []
        }

    results = [score_single_url(url) for url in urls]
    scores = [r["final_probability"] for r in results]

    all_reasons = []
    seen = set()
    for r in results:
        for reason in r["reasons"]:
            if reason not in seen:
                seen.add(reason)
                all_reasons.append(reason)

    return {
        "urls": results,
        "max_url_score": round(max(scores), 4),
        "avg_url_score": round(sum(scores) / len(scores), 4),
        "url_reasons": all_reasons
    }