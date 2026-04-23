from time import perf_counter
from typing import Literal
import base64

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.services.email_analyzer import analyze_email
from app.services.job_detector_service import analyze_job_text
from app.services.ocr_service import (
    extract_text_from_image_bytes,
    extract_ocr_from_attachments,
)

app = FastAPI(
    title="CyberSecure AI API",
    description=(
        "Local FastAPI service for phishing email analysis, "
        "fake job post detection, and OCR-based image analysis. "
        "Use `/docs` to test the endpoints interactively in Swagger UI."
    ),
    version="1.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response Models ─────────────────────────────────────────────────

class AttachmentInput(BaseModel):
    filename: str = Field(default="", description="Attachment filename.")
    content_type: str = Field(default="", description="Attachment MIME type.")
    data_base64: str = Field(default="", description="Base64-encoded attachment bytes.")


class EmailRequest(BaseModel):
    subject: str = Field(default="", description="Email subject line.")
    sender: str = Field(default="", description="Sender email address or display name.")
    body_text: str = Field(default="", description="Plain-text email content.")
    html_text: str = Field(default="", description="Raw HTML email body, if available.")
    attachments: list[AttachmentInput] = Field(
        default_factory=list,
        description="Optional image attachments for OCR analysis.",
    )


class UrlCheckRequest(BaseModel):
    url: str = Field(..., description="URL to analyze for phishing risk.")


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


def decode_attachments(attachments: list[AttachmentInput]) -> list[dict]:
    decoded = []

    for att in attachments:
        raw = b""
        if att.data_base64:
            try:
                raw = base64.b64decode(att.data_base64)
            except Exception:
                raw = b""

        decoded.append(
            {
                "filename": att.filename,
                "content_type": att.content_type,
                "data": raw,
            }
        )

    return decoded


# ── Health / Root ─────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "message": "CyberSecure AI API is running",
        "version": "1.2.0",
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

    decoded_attachments = decode_attachments(request.attachments)
    ocr_text = extract_ocr_from_attachments(decoded_attachments)

    result = analyze_email(
        subject=request.subject,
        sender=request.sender,
        body_text=request.body_text,
        html_text=request.html_text,
        ocr_image_text=ocr_text,
        attachments=decoded_attachments,
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
    start = perf_counter()
    data = await file.read()
    ocr_text = extract_text_from_image_bytes(data)

    result = analyze_email(
        subject="",
        sender="",
        body_text="",
        html_text="",
        ocr_image_text=ocr_text,
        attachments=[],
    )

    result["ocr_text"] = ocr_text
    result["source"] = "image_ocr"
    result["filename"] = file.filename or "unknown"
    result["latency_ms"] = round((perf_counter() - start) * 1000, 2)
    return result


# ── URL Intelligence ─────────────────────────────────────────────────────────

@app.post(
    "/check-url",
    tags=["URL Intelligence"],
    summary="Analyze a URL for phishing risk",
)
def check_url(request: UrlCheckRequest):
    from app.services.url_intelligence_service import analyze_urls

    result = analyze_urls(request.url)
    if not result["urls"]:
        return {
            "url": request.url,
            "risk_score": 0.0,
            "label": "low_risk",
            "reasons": [],
            "details": [],
        }

    score = result["max_url_score"]
    label = "high_risk" if score >= 0.7 else "medium_risk" if score >= 0.4 else "low_risk"

    return {
        "url": request.url,
        "risk_score": round(score, 4),
        "label": label,
        "reasons": result["url_reasons"],
        "details": result["urls"],
    }


# ── Job Scam Detection ────────────────────────────────────────────────────────

@app.post(
    "/analyze-jd",
    tags=["Job Detection"],
    summary="Analyze a job description for fake job indicators",
    response_model=JobDetectionResponse,
)
def analyze_jd(request: JobDescriptionRequest):
    return analyze_job_text(request.text)