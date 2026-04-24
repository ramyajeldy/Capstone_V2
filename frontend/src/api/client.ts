import type {
  EmailAnalysisRequest,
  EmailAnalysisResponse,
  ImageAnalysisResponse,
  OcrResponse,
  JobAnalysisRequest,
  JobAnalysisResponse,
  UrlCheckRequest,
  UrlCheckResponse,
  RiskLabel,
  DetectedUrl,
} from '../types/api';

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

async function post<T>(endpoint: string, body: unknown): Promise<T> {
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API error ${response.status}: ${text}`);
  }
  return response.json() as Promise<T>;
}

async function postFile<T>(endpoint: string, file: File): Promise<T> {
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API error ${response.status}: ${text}`);
  }
  return response.json() as Promise<T>;
}

export async function analyzeEmail(
  request: EmailAnalysisRequest
): Promise<EmailAnalysisResponse> {
  return post<EmailAnalysisResponse>('/analyze', request);
}

/** OCR only — extract text from image without running phishing analysis */
export async function ocrImage(file: File): Promise<OcrResponse> {
  return postFile<OcrResponse>('/ocr', file);
}

/** OCR + full phishing analysis pipeline in one call */
export async function analyzeImage(file: File): Promise<ImageAnalysisResponse> {
  return postFile<ImageAnalysisResponse>('/analyze-image', file);
}

export async function analyzeJobDescription(
  request: JobAnalysisRequest
): Promise<JobAnalysisResponse> {
  return post<JobAnalysisResponse>('/analyze-jd', request);
}

export async function checkUrl(request: UrlCheckRequest): Promise<UrlCheckResponse> {
  // /check-url is not on Cloud Run yet — route through /analyze which runs the same URL intelligence engine
  const res = await post<EmailAnalysisResponse>('/analyze', {
    subject: '',
    sender: '',
    body_text: request.url,
    html_text: '',
  });
  const score = res.url_score;
  const label: RiskLabel =
    score >= 0.7 ? 'high_risk' : score >= 0.4 ? 'medium_risk' : 'low_risk';
  return {
    url: request.url,
    risk_score: score,
    label,
    reasons: res.url_reasons,
    details: res.urls.filter((u): u is DetectedUrl => typeof u !== 'string'),
  };
}

/*
 * GMAIL ADD-ON INTEGRATION NOTE
 * ==============================
 * This client does NOT implement Gmail API access.
 * Gmail fetching is handled exclusively by the Gmail Add-on (separate project).
 * Do NOT add Gmail OAuth or GmailApp calls here.
 */
