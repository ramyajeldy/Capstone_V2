from pathlib import Path
import logging

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_DIR = BASE_DIR / "models" / "phishing_bert_final"
THRESHOLD = 0.12

REQUIRED_MODEL_FILES = (
    "config.json",
    "tokenizer_config.json",
    "tokenizer.json",
)
WEIGHTS_FILE_CANDIDATES = (
    "model.safetensors",
    "pytorch_model.bin",
)


class ModelLoadError(RuntimeError):
    """Raised when a local model cannot be loaded."""


class ModelInferenceError(RuntimeError):
    """Raised when model inference cannot complete."""


tokenizer = None
model = None
load_error = None
last_inference_ok = False
last_inference_error = None


def _required_files_present() -> bool:
    return all((MODEL_DIR / filename).exists() for filename in REQUIRED_MODEL_FILES) and any(
        (MODEL_DIR / filename).exists() for filename in WEIGHTS_FILE_CANDIDATES
    )


def get_model_status() -> dict:
    return {
        "loaded": tokenizer is not None and model is not None and load_error is None,
        "load_error": load_error,
        "model_path": str(MODEL_DIR.resolve()),
        "required_files_present": _required_files_present(),
        "last_inference_ok": last_inference_ok,
        "last_inference_error": last_inference_error,
        "threshold": THRESHOLD,
    }


def load_model(force_reload: bool = False):
    global tokenizer, model, load_error

    if force_reload:
        tokenizer = None
        model = None
        load_error = None

    if tokenizer is not None and model is not None and load_error is None:
        return tokenizer, model

    if not _required_files_present():
        load_error = (
            f"Required phishing model files are missing from {MODEL_DIR}"
        )
        logger.error(load_error)
        raise ModelLoadError(load_error)

    try:
        logger.info("Loading BERT tokenizer from: %s", MODEL_DIR)
        loaded_tokenizer = AutoTokenizer.from_pretrained(
            str(MODEL_DIR),
            local_files_only=True,
        )

        logger.info("Loading BERT model from: %s", MODEL_DIR)
        loaded_model = AutoModelForSequenceClassification.from_pretrained(
            str(MODEL_DIR),
            local_files_only=True,
        )
        loaded_model.eval()
    except Exception as exc:
        tokenizer = None
        model = None
        load_error = str(exc)
        logger.exception("Failed to load phishing BERT model: %s", exc)
        raise ModelLoadError(load_error) from exc

    tokenizer = loaded_tokenizer
    model = loaded_model
    load_error = None
    logger.info("BERT tokenizer and model loaded successfully")
    return tokenizer, model


def get_bert_score(text: str) -> dict:
    global last_inference_ok, last_inference_error

    clean_text = (text or "").strip()
    if not clean_text:
        last_inference_ok = False
        last_inference_error = "Cannot run phishing inference on empty text."
        raise ModelInferenceError(last_inference_error)

    active_tokenizer, active_model = load_model()
    logger.info("Running BERT inference | text_length=%s", len(clean_text))

    try:
        inputs = active_tokenizer(
            clean_text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )

        with torch.no_grad():
            outputs = active_model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=1)
    except Exception as exc:
        last_inference_ok = False
        last_inference_error = str(exc)
        logger.exception("Phishing BERT inference failed: %s", exc)
        raise ModelInferenceError(last_inference_error) from exc

    phishing_prob = float(probs[0][1].item())
    confidence = float(torch.max(probs[0]).item())
    label = "high_risk" if phishing_prob >= THRESHOLD else "low_risk"

    last_inference_ok = True
    last_inference_error = None

    logger.info(
        "BERT inference completed | phishing_prob=%.4f | confidence=%.4f | threshold=%.2f | label=%s",
        phishing_prob,
        confidence,
        THRESHOLD,
        label,
    )

    return {
        "bert_score": round(phishing_prob, 4),
        "confidence": round(confidence, 4),
        "label": label,
    }
