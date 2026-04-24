import base64

from fastapi.testclient import TestClient

from app import main
from app.services import bert_service, job_detector_service, ocr_service


def _ready_health(model_path: str) -> dict:
    return {
        "loaded": True,
        "load_error": None,
        "model_path": model_path,
        "required_files_present": True,
        "last_inference_ok": True,
        "last_inference_error": None,
        "threshold": 0.12,
    }


def _not_ready_health(model_path: str, message: str) -> dict:
    return {
        "loaded": False,
        "load_error": message,
        "model_path": model_path,
        "required_files_present": False,
        "last_inference_ok": False,
        "last_inference_error": None,
        "threshold": 0.12,
    }


def _build_client(monkeypatch, phishing_health=None, job_health=None):
    phishing_health = phishing_health or _ready_health("models/phishing_bert_final")
    job_health = job_health or {
        **_ready_health("models/jobs_detector_model"),
        "threshold": 0.35,
        "device": "cpu",
    }

    def fake_phishing_health():
        return phishing_health

    def fake_job_health():
        return job_health

    def fake_phishing_load():
        if not phishing_health["loaded"]:
            raise bert_service.ModelLoadError(phishing_health["load_error"])
        return object(), object()

    def fake_job_load():
        if not job_health["loaded"]:
            raise job_detector_service.JobModelLoadError(job_health["load_error"])
        return object(), object()

    monkeypatch.setattr(main.bert_service, "get_model_status", fake_phishing_health)
    monkeypatch.setattr(main.bert_service, "load_model", fake_phishing_load)
    monkeypatch.setattr(main.job_detector_service, "get_model_status", fake_job_health)
    monkeypatch.setattr(main.job_detector_service, "load_job_detector", fake_job_load)

    return TestClient(main.app)


def test_health_models_reports_ready_models(monkeypatch):
    client = _build_client(monkeypatch)

    with client as test_client:
        response = test_client.get("/health/models")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["phishing_bert"]["status"] == "ready"
    assert payload["job_detector"]["status"] == "ready"


def test_analyze_returns_503_when_phishing_model_unavailable(monkeypatch):
    client = _build_client(
        monkeypatch,
        phishing_health=_not_ready_health(
            "models/phishing_bert_final",
            "Required phishing model files are missing.",
        ),
    )

    with client as test_client:
        response = test_client.post(
            "/analyze",
            json={"subject": "urgent payroll update", "body_text": "click now"},
        )

    assert response.status_code == 503
    payload = response.json()
    assert payload["code"] == "model_not_ready"
    assert payload["model"] == "phishing_bert_final"


def test_analyze_returns_500_when_phishing_inference_fails(monkeypatch):
    client = _build_client(monkeypatch)

    def fake_analyze_email(**kwargs):
        raise bert_service.ModelInferenceError("phishing inference failed")

    monkeypatch.setattr(main, "analyze_email", fake_analyze_email)

    with client as test_client:
        response = test_client.post(
            "/analyze",
            json={"subject": "invoice", "body_text": "review attached file"},
        )

    assert response.status_code == 500
    payload = response.json()
    assert payload["code"] == "model_inference_failed"
    assert payload["model"] == "phishing_bert_final"


def test_analyze_jd_returns_503_when_job_model_unavailable(monkeypatch):
    client = _build_client(
        monkeypatch,
        job_health={
            **_not_ready_health(
                "models/jobs_detector_model",
                "Required job detector model files are missing.",
            ),
            "threshold": 0.35,
            "device": "cpu",
        },
    )

    with client as test_client:
        response = test_client.post("/analyze-jd", json={"text": "remote work offer"})

    assert response.status_code == 503
    payload = response.json()
    assert payload["code"] == "model_not_ready"
    assert payload["model"] == "jobs_detector_model"


def test_analyze_jd_returns_500_when_job_inference_fails(monkeypatch):
    client = _build_client(monkeypatch)

    def fake_analyze_job_text(_text):
        raise job_detector_service.JobModelInferenceError("job inference failed")

    monkeypatch.setattr(main.job_detector_service, "analyze_job_text", fake_analyze_job_text)

    with client as test_client:
        response = test_client.post("/analyze-jd", json={"text": "suspicious offer"})

    assert response.status_code == 500
    payload = response.json()
    assert payload["code"] == "model_inference_failed"
    assert payload["model"] == "jobs_detector_model"


def test_extract_ocr_from_attachments_uses_decoded_bytes(monkeypatch):
    captured = {}

    def fake_extract_text_from_image_bytes(image_bytes: bytes) -> str:
        captured["bytes"] = image_bytes
        return "decoded text"

    monkeypatch.setattr(ocr_service, "extract_text_from_image_bytes", fake_extract_text_from_image_bytes)

    attachments = main.decode_attachments(
        [
            main.AttachmentInput(
                filename="proof.png",
                content_type="image/png",
                data_base64=base64.b64encode(b"abc123").decode("utf-8"),
            )
        ]
    )

    text = ocr_service.extract_ocr_from_attachments(attachments)

    assert captured["bytes"] == b"abc123"
    assert text == "decoded text"
