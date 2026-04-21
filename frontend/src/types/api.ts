export type RiskLabel = 'high_risk' | 'medium_risk' | 'low_risk';
export type JobLabel = 'fake_job' | 'legitimate_job' | 'unknown';

export interface EmailAnalysisRequest {
  subject: string;
  sender: string;
  body_text: string;
  html_text: string;
}

export interface DetectedUrl {
  url: string;
  domain?: string;
  is_suspicious?: boolean;
  prediction?: string;
  reason?: string;
}

export interface EmailAnalysisResponse {
  risk_score: number;
  confidence: number;
  label: RiskLabel;
  bert_score: number;
  url_score: number;
  html_score: number;
  html_signals: string[];
  url_reasons: string[];
  urls: (string | DetectedUrl)[];
  latency_ms: number;
}

/** Returned by POST /analyze-image — superset of EmailAnalysisResponse */
export interface ImageAnalysisResponse extends EmailAnalysisResponse {
  ocr_text: string;
  source: 'image_ocr';
  filename: string;
}

export interface OcrResponse {
  text: string;
  char_count: number;
  filename: string;
}

export interface JobAnalysisRequest {
  text: string;
}

export interface JobAnalysisResponse {
  label: JobLabel;
  is_fake_job: boolean;
  fraud_probability: number;
  legitimate_probability: number;
  confidence: number;
  threshold_used: number;
  message?: string;
}
