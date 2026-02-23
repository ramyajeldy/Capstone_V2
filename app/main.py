from fastapi import FastAPI
from pydantic import BaseModel
from app.predictor import predict_email

app = FastAPI(title="Phishing Detection API")

class EmailRequest(BaseModel):
    text: str

@app.get("/")
def root():
    return {"status": "API is running"}

@app.post("/predict")
def predict(request: EmailRequest):
    return predict_email(request.text)

@app.get("/health")
def health():
    return {"status": "healthy"}

