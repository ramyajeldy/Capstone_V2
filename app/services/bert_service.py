# app/services/bert_service.py

import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

EMAIL_MODEL_PATH = "models/phishing_bert_final"

device = torch.device("cpu")

class BertEmailService:
    def __init__(self, model_path: str = EMAIL_MODEL_PATH):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.to(device)
        self.model.eval()

    def predict_risk(self, text: str) -> float:
        if not text or not text.strip():
            return 0.0

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )

        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=1)

        # assuming class 1 = phishing/fake
        risk_score = probs[0][1].item()
        return round(float(risk_score), 4)