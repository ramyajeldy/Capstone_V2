import { useState } from 'react';

interface JsonViewerProps {
  data: unknown;
  title?: string;
}

export function JsonViewer({ data, title = 'Raw Response' }: JsonViewerProps) {
  const [open, setOpen] = useState(false);

  return (
    <div className="json-viewer">
      <button className="json-toggle" onClick={() => setOpen(!open)}>
        <span className="json-chevron">{open ? '▼' : '▶'}</span>
        <span>{title}</span>
        <span className="json-badge">JSON</span>
      </button>
      {open && (
        <pre className="json-content">{JSON.stringify(data, null, 2)}</pre>
      )}
    </div>
  );
}
