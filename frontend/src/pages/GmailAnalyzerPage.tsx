import { useState, useEffect } from 'react';
import type { EmailAnalysisRequest, EmailAnalysisResponse } from '../types/api';
import { analyzeEmail } from '../api/client';
import { ResultCard } from '../components/ResultCard';
import { LoadingSpinner } from '../components/LoadingSpinner';

const EMPTY_FORM: EmailAnalysisRequest = { subject: '', sender: '', body_text: '', html_text: '' };

export function GmailAnalyzerPage() {
  const [form, setForm] = useState<EmailAnalysisRequest>(EMPTY_FORM);
  const [result, setResult] = useState<EmailAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fromAddon, setFromAddon] = useState(false);

  const analyze = async (data: EmailAnalysisRequest) => {
    if (!data.body_text.trim() && !data.html_text.trim()) {
      setError('Please provide at least the email body.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await analyzeEmail(data);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const subject = params.get('subject') ?? '';
    const sender  = params.get('sender')  ?? '';
    const body    = params.get('body')    ?? '';
    const html    = params.get('html')    ?? '';

    if (subject || sender || body || html) {
      const emailData: EmailAnalysisRequest = { subject, sender, body_text: body, html_text: html };
      setFromAddon(true);
      setForm(emailData);
      analyze(emailData);
    }
  }, []);

  const handleChange =
    (field: keyof EmailAnalysisRequest) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const handleClear = () => {
    setForm(EMPTY_FORM);
    setResult(null);
    setError(null);
    setFromAddon(false);
    window.history.replaceState({}, '', window.location.pathname);
  };

  return (
    <div className="page-layout">
      {/* ── INPUT PANEL ── */}
      <div className="panel">
        <div className="panel-header">
          <h2 className="panel-title">Gmail Email Analyzer</h2>
          <p className="panel-desc">Detect phishing in any Gmail message using AI</p>
        </div>
        <div className="panel-body">

          {fromAddon ? (
            <div className="addon-connected">
              <span className="addon-dot" />
              <span>Email received from Gmail Add-on</span>
            </div>
          ) : (
            <div className="gmail-cta">
              <div className="gmail-cta-icon">📬</div>
              <button
                className="btn btn-gmail-open"
                onClick={() => window.open('https://mail.google.com', '_blank')}
              >
                Open Gmail
              </button>
              <p className="gmail-cta-sub">or paste email content below</p>
            </div>
          )}

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
              placeholder="Paste email content here…"
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
              rows={3}
              placeholder="Raw HTML email body…"
              value={form.html_text}
              onChange={handleChange('html_text')}
            />
          </div>

          <div className="button-group">
            <button
              className="btn btn-primary"
              onClick={() => analyze(form)}
              disabled={loading}
            >
              {loading ? <LoadingSpinner size="sm" /> : <span>🔍</span>}
              {loading ? 'Analyzing…' : 'Analyze Email'}
            </button>
            <button className="btn btn-secondary" onClick={handleClear} disabled={loading}>
              Clear
            </button>
          </div>
        </div>
      </div>

      {/* ── RESULTS PANEL ── */}
      <div className="panel">
        <div className="panel-header">
          <h2 className="panel-title">Analysis Results</h2>
          <p className="panel-desc">AI risk assessment · BERT + URL + HTML signals</p>
        </div>
        <div className="panel-body">
          {!result && !loading && !error && (
            <div className="empty-state">
              <div className="empty-icon">🛡️</div>
              <p>Submit an email to see the phishing risk assessment.</p>
              <p className="empty-hint">Results appear here instantly after analysis.</p>
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
