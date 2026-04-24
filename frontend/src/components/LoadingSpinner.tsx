interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
}

const SIZE_MAP = { sm: 16, md: 24, lg: 40 };

export function LoadingSpinner({ size = 'md', text }: LoadingSpinnerProps) {
  const px = SIZE_MAP[size];
  return (
    <div className="spinner-wrapper">
      <div
        className="spinner"
        style={{ width: px, height: px, borderWidth: size === 'lg' ? 3 : 2 }}
      />
      {text && <span className="spinner-text">{text}</span>}
    </div>
  );
}
