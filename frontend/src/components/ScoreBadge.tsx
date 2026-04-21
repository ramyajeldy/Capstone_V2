import type { RiskLabel } from '../types/api';

interface ScoreBadgeProps {
  label: RiskLabel;
  score?: number;
}

const LABEL_CONFIG: Record<RiskLabel, { text: string; cls: string }> = {
  high_risk: { text: 'HIGH RISK', cls: 'badge-danger' },
  medium_risk: { text: 'MEDIUM RISK', cls: 'badge-warning' },
  low_risk: { text: 'LOW RISK', cls: 'badge-success' },
};

export function ScoreBadge({ label, score }: ScoreBadgeProps) {
  const { text, cls } = LABEL_CONFIG[label];
  return (
    <div className={`score-badge ${cls}`}>
      <span className="badge-label">{text}</span>
      {score !== undefined && (
        <span className="badge-score">{Math.round(score * 100)}%</span>
      )}
    </div>
  );
}
