from dataclasses import asdict
from pathlib import Path
from app.utils.url_extractor import extract_urls
from url_intelligence_module import URLIntelligenceModel

BASE_DIR = Path(__file__).resolve().parents[2]
URL_MODEL_DIR = BASE_DIR / "models" / "bert_url_model"

url_model = URLIntelligenceModel(model_dir=str(URL_MODEL_DIR))

try:
    url_model.extractor.refresh_openphish()
except Exception:
    pass


def analyze_urls(text: str) -> dict:
    urls = extract_urls(text)

    if not urls:
        return {
            "urls": [],
            "max_url_score": 0.0,
            "avg_url_score": 0.0,
            "url_reasons": []
        }

    results = []
    all_reasons = []

    for url in urls:
        result = url_model.predict_url(url)
        results.append(result)
        all_reasons.extend(result.reasons)

    probabilities = [r.final_probability for r in results]

    unique_reasons = []
    seen = set()
    for reason in all_reasons:
        if reason not in seen:
            seen.add(reason)
            unique_reasons.append(reason)

    return {
        "urls": [asdict(r) for r in results],
        "max_url_score": round(max(probabilities), 4),
        "avg_url_score": round(sum(probabilities) / len(probabilities), 4),
        "url_reasons": unique_reasons
    }