from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_DIR = BASE_DIR / "models" / "phishing_bert_final"

tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR), local_files_only=True)
model = AutoModelForSequenceClassification.from_pretrained(str(MODEL_DIR), local_files_only=True)
model.eval()

THRESHOLD = 0.75

def get_bert_score(text: str) -> dict:
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=256
    )

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=1)

    phishing_prob = float(probs[0][1].item())
    confidence = float(torch.max(probs[0]).item())

    return {
        "bert_score": round(phishing_prob, 4),
        "confidence": round(confidence, 4),
        "label": "high_risk" if phishing_prob >= THRESHOLD else "low_risk"
    }