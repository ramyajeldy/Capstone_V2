import { useState } from 'react';
import { Header } from './components/Header';
import { Tabs } from './components/Tabs';
import { GmailAnalyzerPage } from './pages/GmailAnalyzerPage';
import { JobDetectorPage } from './pages/JobDetectorPage';
import { UrlCheckerPage } from './pages/UrlCheckerPage';
import { EducationPage } from './pages/EducationPage';

type TabId = 'gmail' | 'job' | 'url' | 'education';

export default function App() {
  const [activeTab, setActiveTab] = useState<TabId>('gmail');

  return (
    <div className="app">
      <Header />
      <Tabs active={activeTab} onChange={(id) => setActiveTab(id as TabId)} />
      <main className="main-content">
        {activeTab === 'gmail' && <GmailAnalyzerPage />}
        {activeTab === 'job' && <JobDetectorPage />}
        {activeTab === 'url' && <UrlCheckerPage />}
        {activeTab === 'education' && <EducationPage />}
      </main>
      <footer className="footer">
        <p>
          CyberSecure AI · Powered by BERT ·{' '}
          <a
            href="https://phishing-api-demo-777140345679.us-central1.run.app/docs"
            target="_blank"
            rel="noopener noreferrer"
          >
            API Docs ↗
          </a>
        </p>
      </footer>
    </div>
  );
}
