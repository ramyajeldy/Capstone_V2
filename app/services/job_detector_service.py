from functools import lru_cache
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_DIR = BASE_DIR / "models" / "jobs_detector_model"
THRESHOLD = 0.35
MAX_LENGTH = 256
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


@lru_cache(maxsize=1)
def load_job_detector():
    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR), local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(
        str(MODEL_DIR),
        local_files_only=True,
    )
    model.to(DEVICE)
    model.eval()
    return tokenizer, model


def analyze_job_text(text: str) -> dict:
    cleaned_text = (text or "").strip()
    if not cleaned_text:
        return {
            "label": "unknown",
            "is_fake_job": False,
            "fraud_probability": 0.0,
            "legitimate_probability": 0.0,
            "confidence": 0.0,
            "threshold_used": THRESHOLD,
            "model_name": MODEL_DIR.name,
            "message": "Empty input text.",
        }

    tokenizer, model = load_job_detector()
    inputs = tokenizer(
        cleaned_text,
        return_tensors="pt",
        truncation=True,
        padding="max_length",
        max_length=MAX_LENGTH,
    )
    inputs = {key: value.to(DEVICE) for key, value in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        probabilities = torch.softmax(outputs.logits, dim=-1).cpu().numpy()[0]

    legitimate_probability = float(probabilities[0])
    fraud_probability = float(probabilities[1])
    is_fake_job = fraud_probability >= THRESHOLD

    return {
        "label": "fake_job" if is_fake_job else "legitimate_job",
        "is_fake_job": is_fake_job,
        "fraud_probability": round(fraud_probability, 4),
        "legitimate_probability": round(legitimate_probability, 4),
        "confidence": round(max(legitimate_probability, fraud_probability), 4),
        "threshold_used": THRESHOLD,
        "model_name": MODEL_DIR.name,
    }
