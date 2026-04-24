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
  // fields returned by url_intelligence_service
  normalized_url?: string;
  hostname?: string;
  registered_domain?: string;
  transformer_probability?: number;
  final_probability?: number;
  prediction?: string;
  reasons?: string[];
  whois_domain_age_days?: number;
  whois_lookup_ok?: number;
  openphish_exact_match?: number;
  openphish_domain_match?: number;
  // legacy fallback fields
  domain?: string;
  is_suspicious?: boolean;
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
  ocr_text?: string;
  debug?: {
    subject_length: number;
    sender_length: number;
    body_text_length: number;
    html_text_length: number;
    ocr_text_length: number;
    combined_text_length: number;
    combined_text_preview: string;
    url_scan_text_length: number;
    extracted_url_count: number;
    extracted_urls: string[];
    html_signal_count: number;
  };
}

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
  model_name: string;
  message?: string;
}

export interface UrlCheckRequest {
  url: string;
}

export interface UrlCheckResponse {
  url: string;
  risk_score: number;
  label: RiskLabel;
  reasons: string[];
  details: DetectedUrl[];
}
