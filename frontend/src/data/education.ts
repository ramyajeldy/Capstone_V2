export interface EducationSection {
  id: string;
  title: string;
  icon: string;
  content: string;
  tips?: string[];
}

export const educationSections: EducationSection[] = [
  {
    id: 'what-is-phishing',
    title: 'What is Phishing?',
    icon: '🎣',
    content:
      'Phishing is a cyberattack where criminals impersonate trusted entities—banks, tech companies, or government agencies—to steal sensitive information such as passwords, credit card numbers, or personal data. Attackers craft convincing emails, messages, or websites designed to deceive victims into revealing confidential information or installing malware.',
    tips: [
      'Phishing accounts for over 90% of organizational data breaches globally',
      'Spear phishing targets specific individuals using personalized, researched content',
      'Business Email Compromise (BEC) phishing costs organizations billions annually',
    ],
  },
  {
    id: 'social-engineering',
    title: 'Social Engineering Tactics',
    icon: '🧠',
    content:
      'Social engineering exploits human psychology rather than technical vulnerabilities. Attackers build trust by mimicking authority figures, creating familiarity, or appealing to emotions. Common tactics include impersonating IT departments, pretending to be a colleague in need, or fabricating scenarios that demand immediate action.',
    tips: [
      'Always verify unexpected requests through a separate, known-good communication channel',
      'Be skeptical of any request that asks you to bypass normal approval procedures',
      'Attackers research targets on LinkedIn and social media to craft convincing pretexts',
    ],
  },
  {
    id: 'urgency-tactics',
    title: 'Urgency & Fear Tactics',
    icon: '⚠️',
    content:
      'Phishers create artificial urgency to prevent victims from thinking critically. Phrases like "Your account will be closed in 24 hours," "Immediate action required," or "Security breach detected" trigger panic responses. Legitimate organizations rarely demand immediate action via email without providing alternative verification methods.',
    tips: [
      'Pause and verify before acting on any email that creates a sense of urgency',
      'Real companies provide time and multiple contact options for sensitive actions',
      'Fear-inducing subject lines and red warning banners are primary red flags',
    ],
  },
  {
    id: 'fake-invoices',
    title: 'Fake Invoice & Payment Scams',
    icon: '🧾',
    content:
      'Attackers send fraudulent invoices mimicking legitimate vendors or suppliers, often targeting finance departments. The invoice may contain a subtly changed bank account number or include malicious attachments. Business Email Compromise using this technique has caused billions in losses to organizations worldwide.',
    tips: [
      'Always verify invoice details with the vendor via known contact information—not from the email',
      'Check for subtle changes in bank account or routing numbers on every invoice',
      'Require multi-person approval for large payments as a mandatory control',
    ],
  },
  {
    id: 'credential-harvesting',
    title: 'Credential Harvesting',
    icon: '🔑',
    content:
      'Credential harvesting redirects victims to convincing fake login pages that capture usernames and passwords. These pages may be pixel-perfect replicas of Microsoft 365, Google, or banking portals. After entry, victims are often redirected to the real site to avoid suspicion while attackers gain full account access.',
    tips: [
      'Always check the full URL carefully before entering any credentials',
      'Enable MFA on all accounts—stolen passwords alone cannot be used to log in',
      'A password manager will not autofill credentials on fake lookalike domains',
    ],
  },
  {
    id: 'lookalike-domains',
    title: 'Lookalike Domains',
    icon: '🔍',
    content:
      'Attackers register domains that closely resemble legitimate ones using typosquatting (paypa1.com), homoglyph attacks (using visually identical Unicode characters), or subdomain tricks (paypal.com.evil-domain.xyz routes to evil-domain.xyz, not PayPal). Always examine the full domain root before clicking any link.',
    tips: [
      'Check the domain root, not just the beginning of the URL',
      '"paypal.com.secure-login.net" is controlled by secure-login.net, not PayPal',
      'Homoglyph domains substitute visually identical characters from Cyrillic or Greek alphabets',
    ],
  },
  {
    id: 'qr-phishing',
    title: 'QR Code Phishing (Quishing)',
    icon: '📷',
    content:
      'QR phishing, or "quishing," embeds malicious URLs in QR codes sent via email or physical media. Since email security tools scan text links but often not embedded images, these attacks bypass many filters. Scanning a malicious QR code may redirect to a credential harvesting page or trigger a drive-by download.',
    tips: [
      'Use a QR scanner that previews the destination URL before navigating',
      'Be skeptical of any QR code embedded in an unexpected or unsolicited email',
      'Legitimate services rarely require QR code scanning for account verification via email',
    ],
  },
  {
    id: 'fake-job-scams',
    title: 'Fake Job Scams',
    icon: '💼',
    content:
      'Fake job scams post fraudulent listings on job boards or send unsolicited offers with unusually high pay for minimal qualifications. Red flags include upfront payment requests, requests for sensitive personal or banking information during "onboarding," and reshipping roles disguised as legitimate warehouse or logistics jobs.',
    tips: [
      'Legitimate employers never ask for payment to receive a job offer',
      'Verify the company independently—do not use contact information provided in the listing',
      'Salaries far above market rate for entry-level or unskilled work are a strong red flag',
    ],
  },
  {
    id: 'attachment-phishing',
    title: 'Attachment & Image-Based Phishing',
    icon: '📎',
    content:
      'Malicious attachments—PDFs, Word documents, Excel files, or ZIP archives—can deliver malware when opened. Some attackers embed phishing content inside images to evade text-based email scanners. Macro-enabled Office documents are a common vector, as users are socially engineered into clicking "Enable Content," which executes embedded malicious scripts.',
    tips: [
      'Never enable macros in Office documents received from untrusted or unexpected sources',
      'Open suspicious attachments in a sandboxed environment or submit to a service like VirusTotal',
      'Disable JavaScript in PDF readers to reduce the risk from malicious PDF documents',
    ],
  },
  {
    id: 'how-to-verify',
    title: 'How to Verify Suspicious Emails',
    icon: '✅',
    content:
      'When in doubt, verify through independent channels. Do not use any links, phone numbers, or contact information provided within the suspicious email. Navigate directly to the official website by typing the URL, call the official customer service number from a trusted source, or contact the supposed sender through a known-good email address.',
    tips: [
      'Check SPF, DKIM, and DMARC authentication headers — failed authentication is a major red flag',
      'Hover over links to preview the destination before clicking',
      'Forward suspicious emails to your IT or security team rather than interacting with any content',
    ],
  },
  {
    id: 'safe-browsing',
    title: 'Safe Browsing Practices',
    icon: '🛡️',
    content:
      'Adopt a defense-in-depth approach to online security. Use a reputable password manager with unique credentials for every account. Enable multi-factor authentication everywhere possible. Keep browsers and extensions updated to patch known vulnerabilities. Consider DNS-level filtering to block known malicious domains at the network layer.',
    tips: [
      'MFA stops the vast majority of credential-based account takeover attacks',
      'A password manager is essential — humans cannot securely maintain dozens of unique passwords',
      'HTTPS is necessary but not sufficient — phishing sites routinely obtain valid TLS certificates',
      'Only install browser extensions from verified publishers; each extension is a potential attack surface',
    ],
  },
];
