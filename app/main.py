from time import perf_counter
from typing import Literal
import base64
import binascii
import logging
import os

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.services import bert_service, job_detector_service, url_intelligence_service
from app.services.email_analyzer import analyze_email
from app.services.ocr_service import (
    extract_ocr_from_attachments,
    extract_text_from_image_bytes,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CyberSecure AI API",
    description=(
        "FastAPI service for phishing email analysis, "
        "fake job post detection, OCR-based image analysis, "
        "and URL intelligence. Use `/docs` to test the endpoints interactively."
    ),
    version="1.3.0",
)

startup_checked = False
startup_error = None

PHISHING_MODEL_NAME = "phishing_bert_final"
JOB_MODEL_NAME = "jobs_detector_model"
URL_MODEL_NAME = "bert_url_model"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = perf_counter()
    try:
        response = await call_next(request)
    except Exception as exc:
        latency_ms = round((perf_counter() - start) * 1000, 2)
        logger.exception(
            "Unhandled error | path=%s | method=%s | latency_ms=%s | error=%s",
            request.url.path,
            request.method,
            latency_ms,
            str(exc),
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "path": request.url.path,
                "latency_ms": latency_ms,
            },
        )

    latency_ms = round((perf_counter() - start) * 1000, 2)
    response.headers["X-Process-Time-Ms"] = str(latency_ms)

    logger.info(
        "Request completed | path=%s | method=%s | status=%s | latency_ms=%s",
        request.url.path,
        request.method,
        response.status_code,
        latency_ms,
    )
    return response


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
                raw = base64.b64decode(att.data_base64, validate=True)
            except (binascii.Error, ValueError) as exc:
                logger.warning(
                    "Attachment decode failed | filename=%s | content_type=%s | error=%s",
                    att.filename or "",
                    att.content_type or "",
                    str(exc),
                )
                raw = b""

        decoded.append(
            {
                "filename": att.filename or "",
                "content_type": (att.content_type or "").lower().strip(),
                "data": raw,
            }
        )

    return decoded


def _normalize_model_health(model_name: str, health: dict) -> dict:
    loaded = bool(health.get("loaded"))
    required_files_present = bool(health.get("required_files_present"))
    status = "ready" if loaded and required_files_present else "not_ready"

    return {
        "model": model_name,
        "status": status,
        **health,
    }


def get_models_health() -> dict:
    phishing_health = _normalize_model_health(
        PHISHING_MODEL_NAME,
        bert_service.get_model_status(),
    )
    job_health = _normalize_model_health(
        JOB_MODEL_NAME,
        job_detector_service.get_model_status(),
    )
    url_health = _normalize_model_health(
        URL_MODEL_NAME,
        url_intelligence_service.get_model_status(),
    )
    overall_ready = (
        phishing_health["status"] == "ready"
        and job_health["status"] == "ready"
        and url_health["status"] == "ready"
    )

    return {
        "status": "ok" if overall_ready else "degraded",
        "phishing_bert": phishing_health,
        "job_detector": job_health,
        "url_intelligence": url_health,
    }


def _error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    model: str,
    start: float,
):
    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "message": message,
            "model": model,
            "latency_ms": round((perf_counter() - start) * 1000, 2),
        },
    )


def _invalid_input_response(message: str, start: float):
    return JSONResponse(
        status_code=400,
        content={
            "code": "invalid_input",
            "message": message,
            "latency_ms": round((perf_counter() - start) * 1000, 2),
        },
    )


def _ensure_model_ready(model: str, loader, health_getter, start: float):
    health = health_getter()
    if health.get("loaded") and health.get("required_files_present"):
        return None

    try:
        loader()
    except Exception as exc:
        refreshed_health = health_getter()
        message = (
            refreshed_health.get("load_error")
            or str(exc)
            or f"{model} is not available."
        )
        return _error_response(
            status_code=503,
            code="model_not_ready",
            message=message,
            model=model,
            start=start,
        )

    refreshed_health = health_getter()
    if refreshed_health.get("loaded") and refreshed_health.get("required_files_present"):
        return None

    return _error_response(
        status_code=503,
        code="model_not_ready",
        message=refreshed_health.get("load_error") or f"{model} is not available.",
        model=model,
        start=start,
    )


@app.on_event("startup")
def startup_event():
    global startup_checked, startup_error

    logger.info("App startup initiated")
    logger.info("PORT=%s", os.getenv("PORT", "not_set"))

    startup_failures = {}

    for model_name, loader, health_getter in (
        (PHISHING_MODEL_NAME, bert_service.load_model, bert_service.get_model_status),
        (
            JOB_MODEL_NAME,
            job_detector_service.load_job_detector,
            job_detector_service.get_model_status,
        ),
        (
            URL_MODEL_NAME,
            url_intelligence_service.load_url_model,
            url_intelligence_service.get_model_status,
        ),
    ):
        try:
            loader()
            logger.info("%s loaded during startup", model_name)
        except Exception as exc:
            logger.exception("%s failed during startup: %s", model_name, exc)
            startup_failures[model_name] = health_getter().get("load_error") or str(exc)

    startup_checked = True
    startup_error = startup_failures or None
    logger.info("Startup model inspection completed | failures=%s", startup_failures)


@app.get("/")
def root():
    return {
        "message": "CyberSecure AI API is running",
        "version": "1.3.0",
        "docs_url": "/docs",
        "health_url": "/health",
        "models_health_url": "/health/models",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "services": ["phishing_detection", "job_detection", "ocr", "url_intelligence"],
        "startup_checked": startup_checked,
        "startup_error": startup_error,
    }


@app.get("/health/models")
def health_models():
    return {
        **get_models_health(),
        "startup_checked": startup_checked,
        "startup_error": startup_error,
    }


@app.post("/analyze", tags=["Phishing Detection"], summary="Analyze an email for phishing risk")
def analyze(request: EmailRequest):
    start = perf_counter()

    failure = _ensure_model_ready(
        PHISHING_MODEL_NAME,
        bert_service.load_model,
        bert_service.get_model_status,
        start,
    )
    if failure:
        return failure

    decoded_attachments = decode_attachments(request.attachments)
    ocr_text = extract_ocr_from_attachments(decoded_attachments)

    combined_input = " ".join(
        filter(
            None,
            [
                request.subject.strip(),
                request.sender.strip(),
                request.body_text.strip(),
                request.html_text.strip(),
                ocr_text.strip(),
            ],
        )
    )
    if not combined_input:
        return _invalid_input_response(
            "No text available to analyze after parsing the email and attachments.",
            start,
        )

    try:
        result = analyze_email(
            subject=request.subject,
            sender=request.sender,
            body_text=request.body_text,
            html_text=request.html_text,
            ocr_image_text=ocr_text,
            attachments=decoded_attachments,
        )
    except bert_service.ModelLoadError as exc:
        return _error_response(
            status_code=503,
            code="model_not_ready",
            message=str(exc),
            model=PHISHING_MODEL_NAME,
            start=start,
        )
    except bert_service.ModelInferenceError as exc:
        return _error_response(
            status_code=500,
            code="model_inference_failed",
            message=str(exc),
            model=PHISHING_MODEL_NAME,
            start=start,
        )

    result["ocr_text"] = ocr_text
    result["attachment_count"] = len(decoded_attachments)
    result["latency_ms"] = round((perf_counter() - start) * 1000, 2)
    return result


@app.post(
    "/ocr",
    tags=["OCR"],
    summary="Extract text from an image using Tesseract OCR",
)
async def ocr_image(file: UploadFile = File(...)):
    start = perf_counter()
    data = await file.read()
    text = extract_text_from_image_bytes(data)

    return {
        "text": text,
        "char_count": len(text),
        "filename": file.filename or "unknown",
        "latency_ms": round((perf_counter() - start) * 1000, 2),
    }


@app.post(
    "/analyze-image",
    tags=["Phishing Detection"],
    summary="Analyze a screenshot or image for phishing content via OCR",
)
async def analyze_image(file: UploadFile = File(...)):
    start = perf_counter()

    failure = _ensure_model_ready(
        PHISHING_MODEL_NAME,
        bert_service.load_model,
        bert_service.get_model_status,
        start,
    )
    if failure:
        return failure

    data = await file.read()
    ocr_text = extract_text_from_image_bytes(data)
    if not ocr_text.strip():
        return _invalid_input_response(
            "No OCR text could be extracted from the uploaded image.",
            start,
        )

    try:
        result = analyze_email(
            subject="",
            sender="",
            body_text="",
            html_text="",
            ocr_image_text=ocr_text,
            attachments=[],
        )
    except bert_service.ModelLoadError as exc:
        return _error_response(
            status_code=503,
            code="model_not_ready",
            message=str(exc),
            model=PHISHING_MODEL_NAME,
            start=start,
        )
    except bert_service.ModelInferenceError as exc:
        return _error_response(
            status_code=500,
            code="model_inference_failed",
            message=str(exc),
            model=PHISHING_MODEL_NAME,
            start=start,
        )

    result["ocr_text"] = ocr_text
    result["source"] = "image_ocr"
    result["filename"] = file.filename or "unknown"
    result["latency_ms"] = round((perf_counter() - start) * 1000, 2)
    return result


@app.post(
    "/check-url",
    tags=["URL Intelligence"],
    summary="Analyze a URL for phishing risk",
)
def check_url(request: UrlCheckRequest):
    start = perf_counter()
    from app.services.url_intelligence_service import analyze_urls

    result = analyze_urls(request.url)

    if not result["urls"]:
        return {
            "url": request.url,
            "risk_score": 0.0,
            "label": "low_risk",
            "reasons": [],
            "details": [],
            "latency_ms": round((perf_counter() - start) * 1000, 2),
        }

    score = result["max_url_score"]
    label = "high_risk" if score >= 0.7 else "medium_risk" if score >= 0.4 else "low_risk"

    return {
        "url": request.url,
        "risk_score": round(score, 4),
        "label": label,
        "reasons": result["url_reasons"],
        "details": result["urls"],
        "latency_ms": round((perf_counter() - start) * 1000, 2),
    }


@app.post(
    "/analyze-jd",
    tags=["Job Detection"],
    summary="Analyze a job description for fake job indicators",
    response_model=JobDetectionResponse,
)
def analyze_jd(request: JobDescriptionRequest):
    start = perf_counter()

    failure = _ensure_model_ready(
        JOB_MODEL_NAME,
        job_detector_service.load_job_detector,
        job_detector_service.get_model_status,
        start,
    )
    if failure:
        return failure

    if not request.text.strip():
        return _invalid_input_response(
            "Job description text cannot be empty.",
            start,
        )

    try:
        result = job_detector_service.analyze_job_text(request.text)
    except job_detector_service.JobModelLoadError as exc:
        return _error_response(
            status_code=503,
            code="model_not_ready",
            message=str(exc),
            model=JOB_MODEL_NAME,
            start=start,
        )
    except job_detector_service.JobModelInferenceError as exc:
        return _error_response(
            status_code=500,
            code="model_inference_failed",
            message=str(exc),
            model=JOB_MODEL_NAME,
            start=start,
        )

    result["latency_ms"] = round((perf_counter() - start) * 1000, 2)
    return result
