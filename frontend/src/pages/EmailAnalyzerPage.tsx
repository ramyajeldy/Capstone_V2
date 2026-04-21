import { useState } from 'react';
import type { EmailAnalysisRequest, EmailAnalysisResponse } from '../types/api';
import { analyzeEmail } from '../api/client';
import { ResultCard } from '../components/ResultCard';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { samplePhishingEmail, sampleSafeEmail } from '../data/samples';

const EMPTY_FORM: EmailAnalysisRequest = {
  subject: '',
  sender: '',
  body_text: '',
  html_text: '',
};

export function EmailAnalyzerPage() {
  const [form, setForm] = useState<EmailAnalysisRequest>(EMPTY_FORM);
  const [result, setResult] = useState<EmailAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange =
    (field: keyof EmailAnalysisRequest) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const handleClear = () => {
    setForm(EMPTY_FORM);
    setResult(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!form.body_text.trim() && !form.html_text.trim()) {
      setError('Please provide at least an email body or HTML content.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await analyzeEmail(form);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const loadSample = (type: 'phishing' | 'safe') => {
    setForm(type === 'phishing' ? samplePhishingEmail : sampleSafeEmail);
    setResult(null);
    setError(null);
  };

  return (
    <div className="page-layout">
      {/* ── Input Panel ── */}
      <div className="panel">
        <div className="panel-header">
          <h2 className="panel-title">Email Input</h2>
          <p className="panel-desc">Paste email content for AI phishing analysis</p>
        </div>
        <div className="panel-body">
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
            <button className="btn btn-primary" onClick={handleAnalyze} disabled={loading}>
              {loading ? <LoadingSpinner size="sm" /> : <span>🔍</span>}
              {loading ? 'Analyzing…' : 'Analyze Email'}
            </button>
            <button className="btn btn-secondary" onClick={handleClear} disabled={loading}>
              Clear
            </button>
          </div>

          <div className="sample-buttons">
            <span className="sample-label">Load sample:</span>
            <button className="btn btn-sample btn-sample-danger" onClick={() => loadSample('phishing')} disabled={loading}>
              Phishing Email
            </button>
            <button className="btn btn-sample btn-sample-success" onClick={() => loadSample('safe')} disabled={loading}>
              Safe Email
            </button>
          </div>

          {/*
           * GMAIL ADD-ON INTEGRATION POINT
           * ================================
           * This section is a placeholder for the Gmail Add-on (separate project).
           * The Gmail Add-on will handle OAuth, email extraction, and sidebar display.
           * Do NOT add Gmail API / OAuth calls to this file.
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
        </div>
      </div>

      {/* ── Results Panel ── */}
      <div className="panel">
        <div className="panel-header">
          <h2 className="panel-title">Analysis Results</h2>
          <p className="panel-desc">Risk assessment from the AI detection engine</p>
        </div>
        <div className="panel-body">
          {!result && !loading && !error && (
            <div className="empty-state">
              <div className="empty-icon">🛡️</div>
              <p>Submit an email to see the analysis results.</p>
              <p className="empty-hint">Use the sample buttons to try an example.</p>
            </div>
          )}
          {loading && (
            <div className="loading-state">
              <LoadingSpinner size="lg" text="Analyzing email…" />
            </div>
          )}
          {error && !loading && (
            <div className="error-state">
              <span className="error-icon">⚠️</span>
              <p>{error}</p>
            </div>
          )}
          {result && !loading && <ResultCard result={result} />}
        </div>
      </div>
    </div>
  );
}
