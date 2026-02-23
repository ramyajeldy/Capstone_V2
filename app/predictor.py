import os
import threading
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from google.cloud import storage

# ---------------- CONFIG ---------------- #

THRESHOLD = 0.12
BUCKET_NAME = "phishing-model-488304"  # <-- change if needed
MODEL_PREFIX = "phishing_bert_final"
LOCAL_MODEL_PATH = "/tmp/phishing_bert_final"

device = torch.device("cpu")

# Global model objects
model = None
tokenizer = None
model_lock = threading.Lock()


# ---------------- MODEL DOWNLOAD ---------------- #

def download_model_from_gcs():
    """
    Downloads model files from GCS to /tmp if not already present.
    """
    if os.path.exists(os.path.join(LOCAL_MODEL_PATH, "config.json")):
        return

    os.makedirs(LOCAL_MODEL_PATH, exist_ok=True)

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    blobs = bucket.list_blobs(prefix=MODEL_PREFIX)
    print(f"Downloading model files from GCS bucket '{BUCKET_NAME}' with prefix '{MODEL_PREFIX}'...")

    for blob in blobs:
        filename = blob.name.split("/")[-1]
        if filename:
            local_path = os.path.join(LOCAL_MODEL_PATH, filename)
            blob.download_to_filename(local_path)


# ---------------- MODEL LOAD ---------------- #

def load_model():
    """
    Loads model into memory once.
    Thread-safe.
    """
    global model, tokenizer

    if model is not None:
        return

    with model_lock:
        if model is None:
            download_model_from_gcs()

            model = AutoModelForSequenceClassification.from_pretrained(
                LOCAL_MODEL_PATH
            )
            tokenizer = AutoTokenizer.from_pretrained(
                LOCAL_MODEL_PATH
            )

            model.to(device)
            model.eval()


# ---------------- PREDICTION ---------------- #

def predict_email(text: str) -> dict:
    """
    Predict phishing probability for input text.
    """

    if not text or not text.strip():
        return {
            "risk_score": 0.0,
            "confidence": 0.0,
            "label": "invalid_input"
        }

    load_model()

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
    confidence = torch.max(probs[0]).item()

    return {
        "risk_score": round(phishing_prob, 4),
        "confidence": round(confidence, 4),
        "label": "high_risk" if phishing_prob >= THRESHOLD else "low_risk"
    }