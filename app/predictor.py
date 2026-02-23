import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

THRESHOLD = 0.12
MODEL_PATH = "models/phishing_bert_final"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

_model = None
_tokenizer = None


def load_model():
    global _model, _tokenizer

    if _model is None:
        print("🔄 Loading model...")
        _model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

        _model.to(device)
        _model.eval()

        print("✅ Model loaded successfully.")

    return _model, _tokenizer


def predict_email(text: str) -> dict:
    model, tokenizer = load_model()

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=256
    ).to(device)

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=1)

    phishing_prob = probs[0][1].item()

    return {
        "risk_score": round(phishing_prob, 4),
        "confidence": round(max(probs[0]).item(), 4),
        "label": "high_risk" if phishing_prob >= THRESHOLD else "low_risk"
    }