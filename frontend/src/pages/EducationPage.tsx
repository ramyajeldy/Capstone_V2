import { educationSections } from '../data/education';
import { EducationSection } from '../components/EducationSection';

export function EducationPage() {
  return (
    <div className="edu-page">
      <div className="edu-intro">
        <h2 className="edu-intro-title">
          Phishing <span>Awareness</span> Guide
        </h2>
        <p className="edu-intro-desc">
          Understanding how phishing and social engineering attacks work is the first
          line of defense. Explore the topics below to learn how to recognize and
          protect yourself from modern cyber threats.
        </p>
      </div>
      <div className="edu-grid">
        {educationSections.map((section) => (
          <EducationSection key={section.id} section={section} />
        ))}
      </div>
    </div>
  );
}
