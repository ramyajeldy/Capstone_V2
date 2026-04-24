export function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-brand">
          <div className="header-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M12 2L3 7V12C3 16.97 7.02 21.57 12 22.93C16.98 21.57 21 16.97 21 12V7L12 2Z"
                fill="#dbeafe"
                stroke="#2563eb"
                strokeWidth="1.5"
                strokeLinejoin="round"
              />
              <path
                d="M9 12L11 14L15 10"
                stroke="#2563eb"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <div>
            <h1 className="header-title">
              CyberSecure <span>AI</span>
            </h1>
            <p className="header-subtitle">AI-powered phishing &amp; scam detection</p>
          </div>
        </div>
        <div className="header-badge">
          <span className="status-dot" />
          <span>System Online</span>
        </div>
      </div>
    </header>
  );
}
