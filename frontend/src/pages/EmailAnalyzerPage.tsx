import { useState } from 'react';
import type {
  EmailAnalysisRequest,
  EmailAnalysisResponse,
  ImageAnalysisResponse,
} from '../types/api';
import { analyzeEmail, analyzeImage } from '../api/client';
import { ResultCard } from '../components/ResultCard';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ImageUploader } from '../components/ImageUploader';
import { samplePhishingEmail, sampleSafeEmail } from '../data/samples';

type InputMode = 'text' | 'image';

const EMPTY_FORM: EmailAnalysisRequest = {
  subject: '',
  sender: '',
  body_text: '',
  html_text: '',
};

/** Shows the OCR-extracted text above the analysis result when source is image */
function OcrTextPreview({ text, filename }: { text: string; filename: string }) {
  const [expanded, setExpanded] = useState(false);
  const preview = text.length > 300 ? text.slice(0, 300) + '…' : text;

  return (
    <div className="ocr-preview">
      <div className="ocr-preview-header">
        <div className="ocr-preview-title">
          <span className="ocr-icon">🔤</span>
          <span>OCR Extracted Text</span>
          <span className="ocr-badge">from {filename}</span>
        </div>
        <button
          className="ocr-toggle-btn"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? 'Show less' : 'Show all'}
        </button>
      </div>
      <pre className="ocr-preview-text">
        {expanded ? text : preview}
      </pre>
      {!text.trim() && (
        <p className="ocr-no-text">
          No readable text was detected in the image. The analysis is based on
          visual structure patterns.
        </p>
      )}
    </div>
  );
}

export function EmailAnalyzerPage() {
  const [mode, setMode] = useState<InputMode>('text');
  const [form, setForm] = useState<EmailAnalysisRequest>(EMPTY_FORM);
  const [result, setResult] = useState<EmailAnalysisResponse | null>(null);
  const [imageResult, setImageResult] = useState<ImageAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange =
    (field: keyof EmailAnalysisRequest) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const handleClear = () => {
    setForm(EMPTY_FORM);
    setResult(null);
    setImageResult(null);
    setError(null);
  };

  const switchMode = (m: InputMode) => {
    setMode(m);
    setResult(null);
    setImageResult(null);
    setError(null);
  };

  // ── Text analysis ──
  const handleAnalyzeText = async () => {
    if (!form.body_text.trim() && !form.html_text.trim()) {
      setError('Please provide at least an email body or HTML content.');
      return;
    }
    setLoading(true);
    setError(null);
    setImageResult(null);
    try {
      const data = await analyzeEmail(form);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // ── Image analysis ──
  const handleAnalyzeImage = async (file: File) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await analyzeImage(file);
      setImageResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Image analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const loadSample = (type: 'phishing' | 'safe') => {
    setForm(type === 'phishing' ? samplePhishingEmail : sampleSafeEmail);
    setResult(null);
    setImageResult(null);
    setError(null);
  };

  const activeResult: EmailAnalysisResponse | null = imageResult ?? result;

  return (
    <div className="page-layout">
      {/* ── INPUT PANEL ── */}
      <div className="panel">
        <div className="panel-header">
          <h2 className="panel-title">Email Input</h2>
          <p className="panel-desc">Paste text or upload a screenshot for phishing analysis</p>
        </div>
        <div className="panel-body">
          {/* Mode toggle */}
          <div className="mode-toggle">
            <button
              className={`mode-btn ${mode === 'text' ? 'mode-btn-active' : ''}`}
              onClick={() => switchMode('text')}
            >
              <span>📝</span> Text Input
            </button>
            <button
              className={`mode-btn ${mode === 'image' ? 'mode-btn-active' : ''}`}
              onClick={() => switchMode('image')}
            >
              <span>📷</span> Image Upload
              <span className="mode-btn-badge">OCR</span>
            </button>
          </div>

          {/* ── TEXT MODE ── */}
          {mode === 'text' && (
            <>
              <div className="form-group">
                <label className="form-label">Subject</label>
                <input
                  className="form-input"
                  placeholder="Email subject line"
                  value={form.subject}
                  onChange={handleChange('subject')}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Sender</label>
                <input
                  className="form-input"
                  placeholder="sender@example.com"
                  value={form.sender}
                  onChange={handleChange('sender')}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Body Text</label>
                <textarea
                  className="form-textarea"
                  rows={8}
                  placeholder="Plain text email content…"
                  value={form.body_text}
                  onChange={handleChange('body_text')}
                />
              </div>

              <div className="form-group">
                <label className="form-label">
                  HTML Content <span className="form-optional">(optional)</span>
                </label>
                <textarea
                  className="form-textarea form-textarea-sm"
                  rows={4}
                  placeholder="Raw HTML email body…"
                  value={form.html_text}
                  onChange={handleChange('html_text')}
                />
              </div>

              <div className="button-group">
                <button
                  className="btn btn-primary"
                  onClick={handleAnalyzeText}
                  disabled={loading}
                >
                  {loading ? <LoadingSpinner size="sm" /> : <span>🔍</span>}
                  {loading ? 'Analyzing…' : 'Analyze Email'}
                </button>
                <button
                  className="btn btn-secondary"
                  onClick={handleClear}
                  disabled={loading}
                >
                  Clear
                </button>
              </div>

              <div className="sample-buttons">
                <span className="sample-label">Load sample:</span>
                <button
                  className="btn btn-sample btn-sample-danger"
                  onClick={() => loadSample('phishing')}
                  disabled={loading}
                >
                  Phishing Email
                </button>
                <button
                  className="btn btn-sample btn-sample-success"
                  onClick={() => loadSample('safe')}
                  disabled={loading}
                >
                  Safe Email
                </button>
              </div>

              {/*
               * GMAIL ADD-ON INTEGRATION POINT
               * ================================
               * Placeholder — Gmail fetching is handled by the Gmail Add-on (separate project).
               * Do NOT add Gmail OAuth or GmailApp API calls here.
               */}
              <div className="gmail-placeholder">
                <button
                  className="btn btn-gmail"
                  disabled
                  title="Available via Gmail Add-on integration"
                >
                  <span>📬</span>
                  <span>Analyze from Gmail</span>
                  <span className="btn-coming-soon">Coming Soon</span>
                </button>
                <p className="gmail-note">
                  Gmail integration will be available via the dedicated Gmail Add-on.
                  This interface provides manual analysis and backup functionality.
                </p>
              </div>
            </>
          )}

          {/* ── IMAGE MODE ── */}
          {mode === 'image' && (
            <ImageUploader onAnalyze={handleAnalyzeImage} loading={loading} />
          )}
        </div>
      </div>

      {/* ── RESULTS PANEL ── */}
      <div className="panel">
        <div className="panel-header">
          <h2 className="panel-title">Analysis Results</h2>
          <p className="panel-desc">
            {mode === 'image'
              ? 'OCR extraction + AI risk assessment'
              : 'Risk assessment from the AI detection engine'}
          </p>
        </div>
        <div className="panel-body">
          {!activeResult && !loading && !error && (
            <div className="empty-state">
              <div className="empty-icon">{mode === 'image' ? '📷' : '🛡️'}</div>
              <p>
                {mode === 'image'
                  ? 'Upload a screenshot to extract text and analyze for phishing.'
                  : 'Submit an email to see the analysis results.'}
              </p>
              <p className="empty-hint">
                {mode === 'image'
                  ? 'Supports PNG, JPG, WebP — max 10 MB.'
                  : 'Use the sample buttons to try an example.'}
              </p>
            </div>
          )}

          {loading && (
            <div className="loading-state">
              <LoadingSpinner
                size="lg"
                text={mode === 'image' ? 'Running OCR and analysis…' : 'Analyzing email…'}
              />
            </div>
          )}

          {error && !loading && (
            <div className="error-state">
              <span className="error-icon">⚠️</span>
              <p>{error}</p>
            </div>
          )}

          {/* OCR text preview shown only for image results */}
          {imageResult && !loading && (
            <OcrTextPreview
              text={imageResult.ocr_text}
              filename={imageResult.filename}
            />
          )}

          {activeResult && !loading && <ResultCard result={activeResult} />}
        </div>
      </div>
    </div>
  );
}
