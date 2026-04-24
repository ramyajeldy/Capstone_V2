from pathlib import Path
import logging

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_DIR = BASE_DIR / "models" / "jobs_detector_model"
THRESHOLD = 0.35
MAX_LENGTH = 256
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

REQUIRED_MODEL_FILES = (
    "config.json",
    "tokenizer_config.json",
    "tokenizer.json",
)
WEIGHTS_FILE_CANDIDATES = (
    "model.safetensors",
    "pytorch_model.bin",
)


class JobModelLoadError(RuntimeError):
    """Raised when the job detector model cannot be loaded."""


class JobModelInferenceError(RuntimeError):
    """Raised when the job detector cannot score the request."""


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
        "device": str(DEVICE),
    }


def load_job_detector(force_reload: bool = False):
    global tokenizer, model, load_error

    if force_reload:
        tokenizer = None
        model = None
        load_error = None

    if tokenizer is not None and model is not None and load_error is None:
        return tokenizer, model

    if not _required_files_present():
        load_error = f"Required job detector model files are missing from {MODEL_DIR}"
        logger.error(load_error)
        raise JobModelLoadError(load_error)

    try:
        loaded_tokenizer = AutoTokenizer.from_pretrained(
            str(MODEL_DIR),
            local_files_only=True,
        )
        loaded_model = AutoModelForSequenceClassification.from_pretrained(
            str(MODEL_DIR),
            local_files_only=True,
        )
        loaded_model.to(DEVICE)
        loaded_model.eval()
    except Exception as exc:
        tokenizer = None
        model = None
        load_error = str(exc)
        logger.exception("Failed to load job detector model: %s", exc)
        raise JobModelLoadError(load_error) from exc

    tokenizer = loaded_tokenizer
    model = loaded_model
    load_error = None
    logger.info("Job detector model loaded successfully")
    return tokenizer, model


def analyze_job_text(text: str) -> dict:
    global last_inference_ok, last_inference_error

    cleaned_text = (text or "").strip()
    if not cleaned_text:
        last_inference_ok = False
        last_inference_error = "Cannot run job detector inference on empty text."
        raise JobModelInferenceError(last_inference_error)

    active_tokenizer, active_model = load_job_detector()

    try:
        inputs = active_tokenizer(
            cleaned_text,
            return_tensors="pt",
            truncation=True,
            padding="max_length",
            max_length=MAX_LENGTH,
        )
        inputs = {key: value.to(DEVICE) for key, value in inputs.items()}

        with torch.no_grad():
            outputs = active_model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=-1).cpu().numpy()[0]
    except Exception as exc:
        last_inference_ok = False
        last_inference_error = str(exc)
        logger.exception("Job detector inference failed: %s", exc)
        raise JobModelInferenceError(last_inference_error) from exc

    legitimate_probability = float(probabilities[0])
    fraud_probability = float(probabilities[1])
    is_fake_job = fraud_probability >= THRESHOLD

    last_inference_ok = True
    last_inference_error = None

    return {
        "label": "fake_job" if is_fake_job else "legitimate_job",
        "is_fake_job": is_fake_job,
        "fraud_probability": round(fraud_probability, 4),
        "legitimate_probability": round(legitimate_probability, 4),
        "confidence": round(max(legitimate_probability, fraud_probability), 4),
        "threshold_used": THRESHOLD,
        "model_name": MODEL_DIR.name,
    }
