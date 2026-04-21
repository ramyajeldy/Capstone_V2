import { useState } from 'react';
import type { JobAnalysisResponse } from '../types/api';
import { analyzeJobDescription } from '../api/client';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { JsonViewer } from '../components/JsonViewer';
import { sampleFakeJob, sampleLegitimateJob } from '../data/samples';

function ProbabilityBar({
  label,
  value,
  variant,
}: {
  label: string;
  value: number;
  variant: 'danger' | 'success';
}) {
  const pct = Math.round(value * 100);
  return (
    <div className="score-bar-row">
      <span className="score-bar-label">{label}</span>
      <div className="score-bar-track">
        <div className={`score-bar-fill bar-${variant}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="score-bar-value">{pct}%</span>
    </div>
  );
}

function JobResultCard({ result }: { result: JobAnalysisResponse }) {
  const isFake = result.is_fake_job;

  return (
    <div className={`result-card ${isFake ? 'card-danger' : 'card-success'}`}>
      <div className="result-header">
        <div className={`job-verdict ${isFake ? 'verdict-fake' : 'verdict-legit'}`}>
          <span className="verdict-icon">{isFake ? '🚨' : '✅'}</span>
          <span className="verdict-text">
            {isFake ? 'FAKE JOB DETECTED' : 'LEGITIMATE JOB'}
          </span>
        </div>
        <div className="result-meta">
          Confidence: {Math.round(result.confidence * 100)}%
        </div>
      </div>

      <div className="score-bars">
        <ProbabilityBar label="Fraud Probability" value={result.fraud_probability} variant="danger" />
        <ProbabilityBar label="Legitimate Probability" value={result.legitimate_probability} variant="success" />
      </div>

      <div className="job-details">
        <div className="detail-item">
          <span className="detail-label">Classification</span>
          <span className={`detail-value ${isFake ? 'text-danger' : 'text-success'}`}>
            {result.label.replace('_', ' ').toUpperCase()}
          </span>
        </div>
        <div className="detail-item">
          <span className="detail-label">Detection Threshold</span>
          <span className="detail-value">{result.threshold_used}</span>
        </div>
        {result.message && (
          <div className="detail-item detail-full">
            <span className="detail-label">Note</span>
            <span className="detail-value">{result.message}</span>
          </div>
        )}
      </div>

      <div>
        <JsonViewer data={result} title="Full API Response" />
      </div>
    </div>
  );
}

export function JobDetectorPage() {
  const [text, setText] = useState('');
  const [result, setResult] = useState<JobAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCheck = async () => {
    if (text.trim().length < 20) {
      setError('Please provide a job description (at least 20 characters).');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await analyzeJobDescription({ text });
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setText('');
    setResult(null);
    setError(null);
  };

  const loadSample = (type: 'fake' | 'legit') => {
    setText(type === 'fake' ? sampleFakeJob : sampleLegitimateJob);
    setResult(null);
    setError(null);
  };

  return (
    <div className="page-layout">
      {/* ── Input Panel ── */}
      <div className="panel">
        <div className="panel-header">
          <h2 className="panel-title">Job Description Input</h2>
          <p className="panel-desc">Paste a job listing to check for fraud indicators</p>
        </div>
        <div className="panel-body">
          <div className="form-group" style={{ flex: 1 }}>
            <label className="form-label">Job Description</label>
            <textarea
              className="form-textarea"
              rows={18}
              placeholder="Paste the full job description here…"
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
            <span className="char-count">{text.length} characters</span>
          </div>

          <div className="button-group">
            <button className="btn btn-primary" onClick={handleCheck} disabled={loading}>
              {loading ? <LoadingSpinner size="sm" /> : <span>🔍</span>}
              {loading ? 'Analyzing…' : 'Check Job Description'}
            </button>
            <button className="btn btn-secondary" onClick={handleClear} disabled={loading}>
              Clear
            </button>
          </div>

          <div className="sample-buttons">
            <span className="sample-label">Load sample:</span>
            <button className="btn btn-sample btn-sample-danger" onClick={() => loadSample('fake')} disabled={loading}>
              Fake Job
            </button>
            <button className="btn btn-sample btn-sample-success" onClick={() => loadSample('legit')} disabled={loading}>
              Legitimate Job
            </button>
          </div>
        </div>
      </div>

      {/* ── Results Panel ── */}
      <div className="panel">
        <div className="panel-header">
          <h2 className="panel-title">Detection Results</h2>
          <p className="panel-desc">Job scam classification from the AI model</p>
        </div>
        <div className="panel-body">
          {!result && !loading && !error && (
            <div className="empty-state">
              <div className="empty-icon">💼</div>
              <p>Submit a job description to check for scam indicators.</p>
              <p className="empty-hint">Try the sample buttons to see the model in action.</p>
            </div>
          )}
          {loading && (
            <div className="loading-state">
              <LoadingSpinner size="lg" text="Analyzing job description…" />
            </div>
          )}
          {error && !loading && (
            <div className="error-state">
              <span className="error-icon">⚠️</span>
              <p>{error}</p>
            </div>
          )}
          {result && !loading && <JobResultCard result={result} />}
        </div>
      </div>
    </div>
  );
}
