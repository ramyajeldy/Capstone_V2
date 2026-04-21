import type { EmailAnalysisResponse } from '../types/api';
import { ScoreBadge } from './ScoreBadge';
import { UrlList } from './UrlList';
import { JsonViewer } from './JsonViewer';

interface ResultCardProps {
  result: EmailAnalysisResponse;
}

function ScoreBar({ label, value }: { label: string; value: number }) {
  const pct = Math.round(value * 100);
  const fillCls = pct > 70 ? 'bar-danger' : pct > 40 ? 'bar-warning' : 'bar-success';
  return (
    <div className="score-bar-row">
      <span className="score-bar-label">{label}</span>
      <div className="score-bar-track">
        <div className={`score-bar-fill ${fillCls}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="score-bar-value">{pct}%</span>
    </div>
  );
}

export function ResultCard({ result }: ResultCardProps) {
  const cardCls =
    result.label === 'high_risk'
      ? 'card-danger'
      : result.label === 'medium_risk'
      ? 'card-warning'
      : 'card-success';

  return (
    <div className={`result-card ${cardCls}`}>
      {/* Risk summary */}
      <div className="result-header">
        <ScoreBadge label={result.label} score={result.risk_score} />
        <div className="result-meta">
          <span>Confidence: {Math.round(result.confidence * 100)}%</span>
          <span className="meta-sep">·</span>
          <span>{result.latency_ms} ms</span>
        </div>
      </div>

      {/* Model scores */}
      <div className="score-bars">
        <ScoreBar label="BERT Model" value={result.bert_score} />
        <ScoreBar label="URL Analysis" value={result.url_score} />
        <ScoreBar label="HTML Analysis" value={result.html_score} />
      </div>

      {/* HTML signals */}
      {result.html_signals?.length > 0 && (
        <div>
          <h4 className="section-label">HTML Signals</h4>
          <div className="signals-list">
            {result.html_signals.map((sig, i) => (
              <span key={i} className="signal-tag">{sig}</span>
            ))}
          </div>
        </div>
      )}

      {/* URLs */}
      {(result.urls?.length > 0 || result.url_reasons?.length > 0) && (
        <div>
          <UrlList urls={result.urls ?? []} reasons={result.url_reasons} />
        </div>
      )}

      {/* Debug */}
      <div>
        <JsonViewer data={result} title="Full API Response" />
      </div>
    </div>
  );
}
