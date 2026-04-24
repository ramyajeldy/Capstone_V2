from dataclasses import asdict
from pathlib import Path
import logging

from app.utils.url_extractor import extract_urls
from url_intelligence_module import URLIntelligenceModel

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[2]
URL_MODEL_DIR = BASE_DIR / "models" / "bert_url_model"

REQUIRED_MODEL_FILES = (
    "config.json",
    "tokenizer_config.json",
    "tokenizer.json",
)
WEIGHTS_FILE_CANDIDATES = (
    "model.safetensors",
    "pytorch_model.bin",
)


class URLModelLoadError(RuntimeError):
    """Raised when the URL intelligence model cannot be loaded."""


class URLModelInferenceError(RuntimeError):
    """Raised when URL inference cannot be completed."""


url_model = None
load_error = None
last_inference_ok = False
last_inference_error = None
openphish_refresh_ok = False


def _required_files_present() -> bool:
    return all((URL_MODEL_DIR / filename).exists() for filename in REQUIRED_MODEL_FILES) and any(
        (URL_MODEL_DIR / filename).exists() for filename in WEIGHTS_FILE_CANDIDATES
    )


def load_url_model(force_reload: bool = False):
    global url_model, load_error, openphish_refresh_ok

    if force_reload:
        url_model = None
        load_error = None
        openphish_refresh_ok = False

    if url_model is not None and load_error is None:
        return url_model

    if not _required_files_present():
        load_error = f"Required URL intelligence model files are missing from {URL_MODEL_DIR}"
        logger.error(load_error)
        raise URLModelLoadError(load_error)

    try:
        model = URLIntelligenceModel(model_dir=str(URL_MODEL_DIR))
    except Exception as exc:
        url_model = None
        load_error = str(exc)
        logger.exception("Failed to load URL intelligence model: %s", exc)
        raise URLModelLoadError(load_error) from exc

    try:
        model.extractor.refresh_openphish()
        openphish_refresh_ok = True
    except Exception as exc:
        openphish_refresh_ok = False
        logger.warning("OpenPhish refresh failed during URL model load: %s", exc)

    url_model = model
    load_error = None
    logger.info("URL intelligence model loaded successfully")
    return url_model


def get_model_status() -> dict:
    return {
        "loaded": url_model is not None and load_error is None,
        "load_error": load_error,
        "model_path": str(URL_MODEL_DIR.resolve()),
        "required_files_present": _required_files_present(),
        "last_inference_ok": last_inference_ok,
        "last_inference_error": last_inference_error,
        "openphish_refresh_ok": openphish_refresh_ok,
    }


def analyze_urls(text: str) -> dict:
    global last_inference_ok, last_inference_error

    model = load_url_model()
    urls = extract_urls(text)

    if not urls:
        last_inference_ok = True
        last_inference_error = None
        return {
            "urls": [],
            "max_url_score": 0.0,
            "avg_url_score": 0.0,
            "url_reasons": []
        }

    try:
        results = []
        all_reasons = []

        for url in urls:
            result = model.predict_url(url)
            results.append(result)
            all_reasons.extend(result.reasons)

        probabilities = [r.final_probability for r in results]
    except Exception as exc:
        last_inference_ok = False
        last_inference_error = str(exc)
        logger.exception("URL intelligence inference failed: %s", exc)
        raise URLModelInferenceError(last_inference_error) from exc

    unique_reasons = []
    seen = set()
    for reason in all_reasons:
        if reason not in seen:
            seen.add(reason)
            unique_reasons.append(reason)

    last_inference_ok = True
    last_inference_error = None

    return {
        "urls": [asdict(r) for r in results],
        "max_url_score": round(max(probabilities), 4),
        "avg_url_score": round(sum(probabilities) / len(probabilities), 4),
        "url_reasons": unique_reasons
    }
