from fastapi import FastAPI
from pydantic import BaseModel, Field
from app.predictor import predict_email
from threading import Thread
from app.predictor import load_model

app = FastAPI(title="Phishing Detection API")

@app.on_event("startup")
def warmup_model():
    Thread(target=load_model).start()



class EmailRequest(BaseModel):
    text: str = Field(..., example="Click here to verify your account: http://malicious-link.com")


@app.get("/", description="Welcome endpoint that checks if the API is running")
def root():
    return {"status": "API is running"}

@app.post("/predict", description="Predict whether an email is phishing or safe")
def predict(request: EmailRequest):
    return predict_email(request.text)

@app.get("/health", description="Health check endpoint to verify API is operational")
def health():
    return {"status": "healthy"}

