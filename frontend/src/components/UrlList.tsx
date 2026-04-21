import type { DetectedUrl } from '../types/api';

interface UrlListProps {
  urls: (string | DetectedUrl)[];
  reasons?: string[];
}

function normalize(raw: string | DetectedUrl): DetectedUrl {
  if (typeof raw === 'string') {
    try {
      return { url: raw, domain: new URL(raw).hostname };
    } catch {
      return { url: raw, domain: raw };
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
              return (
                <div
                  key={i}
                  className={`url-item ${item.is_suspicious ? 'url-suspicious' : 'url-clean'}`}
                >
                  <div className="url-domain">{item.domain || item.url}</div>
                  <div className="url-full">{item.url}</div>
                  {item.prediction && (
                    <div className="url-prediction">{item.prediction}</div>
                  )}
                  {item.reason && <div className="url-reason">{item.reason}</div>}
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
