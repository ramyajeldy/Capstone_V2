interface Tab {
  id: string;
  label: string;
  icon: string;
}

const TABS: Tab[] = [
  { id: 'gmail', label: 'Analyze Email', icon: '📬' },
  { id: 'job', label: 'Job Scam Detector', icon: '💼' },
  { id: 'url', label: 'URL Checker', icon: '🔗' },
  { id: 'education', label: 'Phishing Awareness', icon: '📚' },
];

interface TabsProps {
  active: string;
  onChange: (id: string) => void;
}

export function Tabs({ active, onChange }: TabsProps) {
  return (
    <nav className="tabs">
      <div className="tabs-container">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            className={`tab-button ${active === tab.id ? 'tab-active' : ''}`}
            onClick={() => onChange(tab.id)}
          >
            <span className="tab-icon">{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>
    </nav>
  );
}
