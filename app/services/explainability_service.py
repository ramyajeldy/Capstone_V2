import numpy as np
import torch
import shap

from app.services.bert_service import tokenizer, model

def predict_proba_text(texts):
    if isinstance(texts, str):
        texts = [texts]

    enc = tokenizer(
        list(texts),
        padding=True,
        truncation=True,
        max_length=256,
        return_tensors="pt"
    )

    with torch.no_grad():
        logits = model(**enc).logits
        probs = torch.softmax(logits, dim=1).cpu().numpy()

    return probs

# build once
explainer = shap.Explainer(predict_proba_text, tokenizer)

def explain_text(text: str, top_k: int = 10) -> list[dict]:
    shap_values = explainer([text])

    class_idx = 1
    values = shap_values[0, :, class_idx]
    tokens = shap_values.data[0]
    impacts = values.values

    skip_tokens = {
        "subject", "sender", "body", "text", "html", "ocr",
        "extracted", "from", "to"
    }

    rows = []

    for token, impact in zip(tokens, impacts):
        token = str(token).strip().lower()

        if not token:
            continue

        if token in skip_tokens:
            continue

        if len(token) <= 2:
            continue

        if not any(ch.isalnum() for ch in token):
            continue

        rows.append({
            "token": token,
            "impact": float(impact)
        })

    rows.sort(key=lambda x: abs(x["impact"]), reverse=True)
    return rows[:top_k]

def explain_text_full(text: str):
    return explainer([text])