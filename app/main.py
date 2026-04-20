from fastapi import FastAPI
from pydantic import BaseModel
from time import perf_counter
from app.services.email_analyzer import analyze_email

app = FastAPI(title="CyberSecure AI - Phishing Analyzer")


class EmailRequest(BaseModel):
    subject: str = ""
    sender: str = ""
    body_text: str = ""
    html_text: str = ""


@app.get("/")
def root():
    return {"message": "CyberSecure AI API is running"}


@app.post("/analyze")
def analyze(request: EmailRequest):
    start = perf_counter()
    

    result = analyze_email(
        subject=request.subject,
        sender=request.sender,
        body_text=request.body_text,
        html_text=request.html_text,
        attachments=[]
    )

    result["latency_ms"] = round((perf_counter() - start) * 1000, 2)
    return result

@app.get("/health")
def health():
    return {"status": "ok"}