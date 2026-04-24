import { useState, useRef, useCallback } from 'react';
import { LoadingSpinner } from './LoadingSpinner';

interface ImageUploaderProps {
  onAnalyze: (file: File) => void;
  loading: boolean;
}

const ACCEPTED_TYPES = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp'];
const MAX_BYTES = 10 * 1024 * 1024; // 10 MB

function formatSize(bytes: number): string {
  return bytes < 1024 * 1024
    ? `${(bytes / 1024).toFixed(1)} KB`
    : `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function ImageUploader({ onAnalyze, loading }: ImageUploaderProps) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const validate = (f: File): string | null => {
    if (!ACCEPTED_TYPES.includes(f.type))
      return 'Only PNG, JPG, or WebP images are supported.';
    if (f.size > MAX_BYTES)
      return 'File size must be under 10 MB.';
    return null;
  };

  const loadFile = useCallback((f: File) => {
    const err = validate(f);
    if (err) { setValidationError(err); return; }
    setValidationError(null);
    setFile(f);
    const url = URL.createObjectURL(f);
    setPreview(url);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const clearFile = () => {
    if (preview) URL.revokeObjectURL(preview);
    setFile(null);
    setPreview(null);
    setValidationError(null);
    if (inputRef.current) inputRef.current.value = '';
  };

  const onDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setDragActive(false);
      const f = e.dataTransfer.files[0];
      if (f) loadFile(f);
    },
    [loadFile]
  );

  const onDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragActive(true);
  };

  return (
    <div className="image-uploader">
      {/* ── Drop zone (shown when no file loaded) ── */}
      {!file && (
        <div
          className={`drop-zone ${dragActive ? 'drop-zone-active' : ''}`}
          onDrop={onDrop}
          onDragOver={onDragOver}
          onDragLeave={() => setDragActive(false)}
          onClick={() => !loading && inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            accept="image/png,image/jpeg,image/jpg,image/webp"
            style={{ display: 'none' }}
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) loadFile(f);
            }}
          />
          <div className="drop-zone-icon">
            {dragActive ? '📂' : '📷'}
          </div>
          <p className="drop-zone-title">
            {dragActive ? 'Release to upload' : 'Drop a screenshot here'}
          </p>
          <p className="drop-zone-hint">
            or click to browse &nbsp;·&nbsp; PNG, JPG, WebP &nbsp;·&nbsp; max 10 MB
          </p>
          <div className="drop-zone-examples">
            <span>Supported: phishing email screenshots</span>
            <span className="dot-sep">·</span>
            <span>scam banners</span>
            <span className="dot-sep">·</span>
            <span>fake login pages</span>
          </div>
        </div>
      )}

      {/* ── File loaded — preview card ── */}
      {file && preview && (
        <div className="image-preview-card">
          <div className="image-preview-left">
            <img
              src={preview}
              alt="Uploaded screenshot preview"
              className="image-preview-thumb"
            />
          </div>
          <div className="image-preview-right">
            <div className="image-preview-meta">
              <span className="image-preview-name" title={file.name}>
                {file.name.length > 36 ? file.name.slice(0, 33) + '…' : file.name}
              </span>
              <div className="image-preview-tags">
                <span className="img-tag">{file.type.split('/')[1].toUpperCase()}</span>
                <span className="img-tag">{formatSize(file.size)}</span>
              </div>
            </div>
            <p className="image-preview-ready">
              ✓ Ready for analysis
            </p>
            <button
              className="btn-image-remove"
              onClick={clearFile}
              disabled={loading}
            >
              ✕ Remove
            </button>
          </div>
        </div>
      )}

      {/* ── Validation error ── */}
      {validationError && (
        <div className="drop-zone-error">
          <span>⚠️</span>
          <span>{validationError}</span>
        </div>
      )}

      {/* ── Action buttons ── */}
      <div className="button-group" style={{ marginTop: 16 }}>
        <button
          className="btn btn-primary"
          onClick={() => file && onAnalyze(file)}
          disabled={!file || loading}
        >
          {loading ? <LoadingSpinner size="sm" /> : <span>🔍</span>}
          {loading ? 'Analyzing…' : 'Analyze Image'}
        </button>
        {file && (
          <button
            className="btn btn-secondary"
            onClick={clearFile}
            disabled={loading}
          >
            Clear
          </button>
        )}
      </div>

      {/* ── Info tip ── */}
      {!file && (
        <div className="uploader-tip">
          <span className="uploader-tip-icon">💡</span>
          <span>
            The image will be processed with OCR (Tesseract) to extract text,
            which is then analyzed by the AI phishing detection model.
            Extracted text will be shown alongside the results.
          </span>
        </div>
      )}
    </div>
  );
}
