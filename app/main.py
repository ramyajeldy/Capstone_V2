from time import perf_counter
from typing import Literal

from fastapi import FastAPI, File, UploadFile

from pydantic import BaseModel, Field

from app.services.email_analyzer import analyze_email
from app.services.job_detector_service import analyze_job_text
from app.services.ocr_service import extract_text_from_image_bytes

app = FastAPI(
    title="CyberSecure AI API",
    description=(
        "Local FastAPI service for phishing email analysis, "
        "fake job post detection, and OCR-based image analysis. "
        "Use `/docs` to test the endpoints interactively in Swagger UI."
    ),
    version="1.1.0",
)


# ── Request / Response Models ─────────────────────────────────────────────────

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


# ── Health / Root ─────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "message": "CyberSecure AI API is running",
        "version": "1.1.0",
        "docs_url": "/docs",
        "health_url": "/health",
    }


@app.get("/health")
def health():
    return {"status": "ok", "services": ["phishing_detection", "job_detection", "ocr"]}


# ── Phishing Detection ────────────────────────────────────────────────────────

@app.post("/analyze", tags=["Phishing Detection"], summary="Analyze an email for phishing risk")
def analyze(request: EmailRequest):
    start = perf_counter()
    result = analyze_email(
        subject=request.subject,
        sender=request.sender,
        body_text=request.body_text,
        html_text=request.html_text,
        attachments=[],
    )
    result["latency_ms"] = round((perf_counter() - start) * 1000, 2)
    return result


# ── OCR & Image Analysis ──────────────────────────────────────────────────────

@app.post(
    "/ocr",
    tags=["OCR"],
    summary="Extract text from an image using Tesseract OCR",
)
async def ocr_image(file: UploadFile = File(...)):
    """
    Upload a PNG, JPG, or WebP image and extract its text content via OCR.
    Returns the raw extracted text and character count.
    """
    data = await file.read()
    text = extract_text_from_image_bytes(data)
    return {
        "text": text,
        "char_count": len(text),
        "filename": file.filename or "unknown",
    }


@app.post(
    "/analyze-image",
    tags=["Phishing Detection"],
    summary="Analyze a screenshot or image for phishing content via OCR",
)
async def analyze_image(file: UploadFile = File(...)):
    """
    Upload an image (screenshot of an email, phishing banner, QR code result, etc.).
    The image is OCR-processed, then the extracted text is run through the full
    phishing analysis pipeline (BERT + URL + HTML scoring).
    """
    start = perf_counter()
    data = await file.read()
    ocr_text = extract_text_from_image_bytes(data)

    result = analyze_email(
        subject="",
        sender="",
        body_text=ocr_text,
        html_text="",
        attachments=[],
    )
    result["ocr_text"] = ocr_text
    result["source"] = "image_ocr"
    result["filename"] = file.filename or "unknown"
    result["latency_ms"] = round((perf_counter() - start) * 1000, 2)
    return result


# ── Job Scam Detection ────────────────────────────────────────────────────────

@app.post(
    "/analyze-jd",
    tags=["Job Detection"],
    summary="Analyze a job description for fake job indicators",
    response_model=JobDetectionResponse,
)
def analyze_jd(request: JobDescriptionRequest):
    return analyze_job_text(request.text)
