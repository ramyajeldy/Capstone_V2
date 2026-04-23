import type { DetectedUrl } from '../types/api';

interface UrlListProps {
  urls: (string | DetectedUrl)[];
  reasons?: string[];
}

function normalize(raw: string | DetectedUrl): DetectedUrl {
  if (typeof raw === 'string') {
    try {
      return { url: raw, hostname: new URL(raw).hostname };
    } catch {
      return { url: raw, hostname: raw };
    }
  }
  return raw;
}

export function UrlList({ urls, reasons }: UrlListProps) {
  if (!urls.length && !reasons?.length) return null;

  return (
    <div>
      {urls.length > 0 && (
        <>
          <h4 className="section-label">Detected URLs</h4>
          <div className="url-list">
            {urls.map((raw, i) => {
              const item = normalize(raw);
              const isSuspicious =
                item.is_suspicious ||
                (item.final_probability !== undefined && item.final_probability >= 0.5) ||
                item.prediction === 'phishing';
              const displayDomain = item.hostname || item.domain || item.url;
              const itemReasons = item.reasons ?? (item.reason ? [item.reason] : []);
              const prob = item.final_probability ?? item.transformer_probability;

              return (
                <div
                  key={i}
                  className={`url-item ${isSuspicious ? 'url-suspicious' : 'url-clean'}`}
                >
                  <div className="url-domain">{displayDomain}</div>
                  <div className="url-full">{item.url}</div>
                  {item.prediction && (
                    <div className="url-prediction">{item.prediction}</div>
                  )}
                  {prob !== undefined && (
                    <div className="url-prob">
                      Risk: {Math.round(prob * 100)}%
                    </div>
                  )}
                  {itemReasons.map((r, j) => (
                    <div key={j} className="url-reason">{r}</div>
                  ))}
                </div>
              );
            })}
          </div>
        </>
      )}

      {reasons && reasons.length > 0 && (
        <div className="url-reasons">
          <h5 className="section-label-sm">URL Risk Reasons</h5>
          <ul>
            {reasons.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
