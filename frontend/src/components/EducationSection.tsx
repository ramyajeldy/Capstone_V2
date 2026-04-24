import { useState } from 'react';
import type { EducationSection as SectionData } from '../data/education';

interface Props {
  section: SectionData;
}

export function EducationSection({ section }: Props) {
  const [open, setOpen] = useState(false);

  return (
    <div className={`edu-section ${open ? 'edu-open' : ''}`}>
      <button className="edu-header" onClick={() => setOpen(!open)}>
        <div className="edu-title">
          <span className="edu-icon">{section.icon}</span>
          <span>{section.title}</span>
        </div>
        <span className={`edu-chevron ${open ? 'chevron-open' : ''}`}>›</span>
      </button>

      {open && (
        <div className="edu-body">
          <p className="edu-content">{section.content}</p>
          {section.tips && section.tips.length > 0 && (
            <div className="edu-tips">
              <h4 className="edu-tips-title">Key Points</h4>
              <ul className="edu-tips-list">
                {section.tips.map((tip, i) => (
                  <li key={i} className="edu-tip">
                    {tip}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
