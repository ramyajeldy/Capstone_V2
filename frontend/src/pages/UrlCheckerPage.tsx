import { useState } from 'react';
import type { UrlCheckResponse } from '../types/api';
import { checkUrl } from '../api/client';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ScoreBadge } from '../components/ScoreBadge';
import { JsonViewer } from '../components/JsonViewer';

function UrlResultCard({ result }: { result: UrlCheckResponse }) {
  const cardCls =
    result.label === 'high_risk'
      ? 'card-danger'
      : result.label === 'medium_risk'
      ? 'card-warning'
      : 'card-success';

  const pct = Math.round(result.risk_score * 100);
  const barCls = pct > 70 ? 'bar-danger' : pct > 40 ? 'bar-warning' : 'bar-success';

  return (
    <div className={`result-card ${cardCls}`}>
      <div className="result-header">
        <ScoreBadge label={result.label} score={result.risk_score} />
      </div>

      <div className="score-bars">
        <div className="score-bar-row">
          <span className="score-bar-label">Risk Score</span>
          <div className="score-bar-track">
            <div className={`score-bar-fill ${barCls}`} style={{ width: `${pct}%` }} />
          </div>
          <span className="score-bar-value">{pct}%</span>
        </div>
      </div>

      <div className="url-checked">
        <span className="detail-label">Checked URL</span>
        <span className="url-checked-value">{result.url}</span>
      </div>

      {result.reasons.length > 0 && (
        <div>
          <h4 className="section-label">Risk Indicators</h4>
          <div className="signals-list">
            {result.reasons.map((r, i) => (
              <span key={i} className="signal-tag">{r}</span>
            ))}
          </div>
        </div>
      )}

      {result.details.length > 0 && (
        <div>
          <JsonViewer data={result.details} title="URL Intelligence Details" />
        </div>
      )}
    </div>
  );
}

const SAMPLE_URLS = [
  { label: 'Suspicious', url: 'http://paypa1-secure-login.tk/verify?account=update' },
  { label: 'Legitimate', url: 'https://www.google.com' },
];

export function UrlCheckerPage() {
  const [url, setUrl] = useState('');
  const [result, setResult] = useState<UrlCheckResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCheck = async () => {
    if (!url.trim()) {
      setError('Please enter a URL to check.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await checkUrl({ url: url.trim() });
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Check failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setUrl('');
    setResult(null);
    setError(null);
  };

  const loadSample = (sampleUrl: string) => {
    setUrl(sampleUrl);
    setResult(null);
    setError(null);
  };

  return (
    <div className="page-layout">
      {/* ── INPUT PANEL ── */}
      <div className="panel">
        <div className="panel-header">
          <h2 className="panel-title">URL Phishing Checker</h2>
          <p className="panel-desc">Paste any URL to check for phishing and malicious indicators</p>
        </div>
        <div className="panel-body">
          <div className="form-group">
            <label className="form-label">URL to Check</label>
            <input
              className="form-input"
              placeholder="https://example.com/login"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleCheck()}
            />
          </div>

          <div className="button-group">
            <button
              className="btn btn-primary"
              onClick={handleCheck}
              disabled={loading}
            >
              {loading ? <LoadingSpinner size="sm" /> : <span>🔗</span>}
              {loading ? 'Checking…' : 'Check URL'}
            </button>
            <button className="btn btn-secondary" onClick={handleClear} disabled={loading}>
              Clear
            </button>
          </div>

          <div className="sample-buttons">
            <span className="sample-label">Load sample:</span>
            {SAMPLE_URLS.map((s) => (
              <button
                key={s.label}
                className={`btn btn-sample ${s.label === 'Suspicious' ? 'btn-sample-danger' : 'btn-sample-success'}`}
                onClick={() => loadSample(s.url)}
                disabled={loading}
              >
                {s.label}
              </button>
            ))}
          </div>

          <div className="url-checker-info">
            <h4 className="section-label">What we check</h4>
            <ul className="url-check-list">
              <li>🎭 Domain spoofing &amp; typosquatting</li>
              <li>📋 Known phishing &amp; malware blacklists</li>
              <li>🔡 Suspicious TLDs and free subdomains</li>
              <li>🔢 IP addresses used as hostnames</li>
              <li>🔗 Excessive redirects and URL shorteners</li>
              <li>🤖 BERT model trained on phishing URLs</li>
            </ul>
          </div>
        </div>
      </div>

      {/* ── RESULTS PANEL ── */}
      <div className="panel">
        <div className="panel-header">
          <h2 className="panel-title">URL Analysis Result</h2>
          <p className="panel-desc">Risk assessment from URL intelligence engine</p>
        </div>
        <div className="panel-body">
          {!result && !loading && !error && (
            <div className="empty-state">
              <div className="empty-icon">🔗</div>
              <p>Enter a URL to check it for phishing indicators.</p>
              <p className="empty-hint">Try the sample buttons to see the model in action.</p>
            </div>
          )}
          {loading && (
            <div className="loading-state">
              <LoadingSpinner size="lg" text="Analyzing URL…" />
            </div>
          )}
          {error && !loading && (
            <div className="error-state">
              <span className="error-icon">⚠️</span>
              <p>{error}</p>
            </div>
          )}
          {result && !loading && <UrlResultCard result={result} />}
        </div>
      </div>
    </div>
  );
}
