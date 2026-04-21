from time import perf_counter
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.services.email_analyzer import analyze_email
from app.services.job_detector_service import analyze_job_text

app = FastAPI(
    title="CyberSecure AI API",
    description=(
        "Local FastAPI service for phishing email analysis and fake job post detection. "
        "Use `/docs` to test the endpoints interactively in Swagger UI."
    ),
    version="1.0.0",
)


class EmailRequest(BaseModel):
    subject: str = Field(default="", description="Email subject line.")
    sender: str = Field(default="", description="Sender email address or display name.")
    body_text: str = Field(default="", description="Plain-text email content.")
    html_text: str = Field(default="", description="Raw HTML email body, if available.")


class JobDescriptionRequest(BaseModel):
    text: str = Field(
        ...,
        description="Job posting text or description to classify.",
        examples=[
            "Work from home and earn $5000 weekly with no experience. Immediate joining. "
            "No interview. Free laptop. Send your bank details to begin."
        ],
    )


class JobDetectionResponse(BaseModel):
    label: Literal["fake_job", "legitimate_job", "unknown"]
    is_fake_job: bool
    fraud_probability: float
    legitimate_probability: float
    confidence: float
    threshold_used: float
    model_name: str
    message: str | None = None


@app.get("/")
def root():
    return {
        "message": "CyberSecure AI API is running",
        "docs_url": "/docs",
        "health_url": "/health",
    }


@app.post("/analyze", tags=["Phishing Detection"], summary="Analyze an email for phishing risk")
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


@app.post(
    "/analyze-jd",
    tags=["Job Detection"],
    summary="Analyze a job description for fake job indicators",
    response_model=JobDetectionResponse,
)
def analyze_jd(request: JobDescriptionRequest):
    return analyze_job_text(request.text)


@app.get("/health")
def health():
    return {"status": "ok", "services": ["phishing_detection", "job_detection"]}
