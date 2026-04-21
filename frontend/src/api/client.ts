import type {
  EmailAnalysisRequest,
  EmailAnalysisResponse,
  JobAnalysisRequest,
  JobAnalysisResponse,
} from '../types/api';

// Centralized API base URL — update here if the backend is redeployed
const BASE_URL = 'https://phishing-api-demo-777140345679.us-central1.run.app';

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

export async function analyzeEmail(
  request: EmailAnalysisRequest
): Promise<EmailAnalysisResponse> {
  return post<EmailAnalysisResponse>('/analyze', request);
}

export async function analyzeJobDescription(
  request: JobAnalysisRequest
): Promise<JobAnalysisResponse> {
  return post<JobAnalysisResponse>('/analyze-jd', request);
}

// Health check utility
export async function checkHealth(): Promise<{ status: string }> {
  const response = await fetch(`${BASE_URL}/health`);
  return response.json() as Promise<{ status: string }>;
}

/*
 * GMAIL ADD-ON INTEGRATION NOTE
 * ==============================
 * This client file intentionally does NOT implement Gmail API access.
 * Gmail fetching will be handled exclusively by the Gmail Add-on (separate project).
 *
 * When the Gmail Add-on is ready, it will:
 *   1. Use Gmail's OAuth2 context within the add-on sidebar
 *   2. Extract subject, sender, body, and headers from the active message
 *   3. Call analyzeEmail() with that extracted data
 *   4. Display the response directly in the Gmail sidebar UI
 *
 * Do NOT add Gmail OAuth, GmailApp, or any Google API calls to this file.
 */
