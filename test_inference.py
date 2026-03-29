import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

THRESHOLD = 0.12

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = AutoModelForSequenceClassification.from_pretrained(
    "models/phishing_bert_final"
)

tokenizer = AutoTokenizer.from_pretrained(
    "models/phishing_bert_final"
)

model.to(device)
model.eval()

def predict_email(text):
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

print(predict_email("Urgent! Verify your bank account now."))