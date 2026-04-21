import { useState } from 'react';
import { Header } from './components/Header';
import { Tabs } from './components/Tabs';
import { EmailAnalyzerPage } from './pages/EmailAnalyzerPage';
import { JobDetectorPage } from './pages/JobDetectorPage';
import { EducationPage } from './pages/EducationPage';

type TabId = 'email' | 'job' | 'education';

export default function App() {
  const [activeTab, setActiveTab] = useState<TabId>('email');

  return (
    <div className="app">
      <Header />
      <Tabs active={activeTab} onChange={(id) => setActiveTab(id as TabId)} />
      <main className="main-content">
        {activeTab === 'email' && <EmailAnalyzerPage />}
        {activeTab === 'job' && <JobDetectorPage />}
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
