import type { EmailAnalysisRequest } from '../types/api';

export const samplePhishingEmail: EmailAnalysisRequest = {
  subject: 'URGENT: Your account has been suspended — Verify now',
  sender: 'security@paypa1-support.com',
  body_text: `Dear Valued Customer,

We have detected unusual activity on your PayPal account. Your account has been temporarily suspended pending verification.

To restore access immediately, you must verify your identity within 24 hours or your account will be permanently closed.

Click here to verify: http://paypal-verify-account.tk/secure/login

WARNING: Failure to verify will result in:
- Account suspension
- Pending transactions cancelled
- Funds held for 180 days

This is an automated security alert. Do not reply to this email.

PayPal Security Team`,
  html_text: `<html><body>
<div style="background:#003087;padding:20px;text-align:center;">
  <h1 style="color:white;">PayPal</h1>
</div>
<div style="padding:20px;font-family:Arial;">
  <p><strong>⚠️ Your account has been suspended</strong></p>
  <p>We detected unusual sign-in activity. Click below to restore access immediately:</p>
  <a href="http://paypal-verify-account.tk/secure/login"
     style="background:#0070ba;color:white;padding:15px 30px;text-decoration:none;display:inline-block;border-radius:5px;">
    Verify My Account Now
  </a>
  <p style="color:red;font-weight:bold;">⚠️ You have 24 hours before permanent suspension</p>
  <p style="font-size:11px;color:#999;">© 2026 PayPal Inc. 2211 North First Street, San Jose, CA 95131</p>
</div>
</body></html>`,
};

export const sampleSafeEmail: EmailAnalysisRequest = {
  subject: 'Your monthly GitHub Copilot invoice — April 2026',
  sender: 'noreply@github.com',
  body_text: `Hi there,

Your GitHub Copilot subscription has been renewed for another month.

Invoice details:
- Plan: GitHub Copilot Individual
- Amount: $10.00 USD
- Date: April 21, 2026
- Invoice #: GH-2026-04-INV-00421

You can view your full invoice and manage billing settings at github.com/settings/billing.

Thanks for using GitHub Copilot!

The GitHub Team`,
  html_text: `<html><body style="font-family:Arial;max-width:600px;margin:0 auto;">
<div style="background:#24292e;padding:20px;text-align:center;">
  <h1 style="color:white;font-size:24px;">GitHub</h1>
</div>
<div style="padding:20px;">
  <h2>Your April Invoice</h2>
  <p>Your GitHub Copilot subscription has been renewed successfully.</p>
  <table style="width:100%;border-collapse:collapse;">
    <tr><td style="padding:8px;border-bottom:1px solid #eee;">Plan</td><td>GitHub Copilot Individual</td></tr>
    <tr><td style="padding:8px;border-bottom:1px solid #eee;">Amount</td><td>$10.00 USD</td></tr>
    <tr><td style="padding:8px;">Date</td><td>April 21, 2026</td></tr>
  </table>
  <p>Manage billing: <a href="https://github.com/settings/billing">github.com/settings/billing</a></p>
</div>
</body></html>`,
};

export const sampleFakeJob = `Job Title: Remote Data Entry Specialist — Work From Home

Salary: $50–$75 per hour, paid weekly via Western Union or gift cards

URGENT HIRING — No experience necessary! We are immediately hiring remote workers worldwide.

Requirements:
- Must have a working computer or smartphone
- Available at least 2 hours per day
- Bank account or PayPal for receiving payments

What you will do:
- Simple data entry tasks from home
- Process customer payments and forward funds
- Receive and reship packages on behalf of clients

To get started, send us your full name, home address, date of birth, and bank account details to jobs@quickhire-remote.biz

IMMEDIATE HIRING — first 50 applicants receive a $500 signing bonus!

Note: You will need to purchase a starter kit ($150 refundable deposit) before you can begin.`;

export const sampleLegitimateJob = `Senior Software Engineer — Backend (Python / FastAPI)

Company: TechCorp Inc. | San Francisco, CA (Hybrid — 2 days onsite)
Salary: $140,000–$180,000 per year + equity + full benefits

About the Role:
We are looking for an experienced backend engineer to join our platform team. You will design and maintain high-traffic REST APIs powering our SaaS product used by 500,000+ customers.

Responsibilities:
- Design and implement scalable APIs using FastAPI and Python
- Own database architecture decisions (PostgreSQL, Redis)
- Collaborate with frontend and ML teams on feature delivery
- Participate in on-call rotation (generous compensation included)

Requirements:
- 4+ years of backend engineering experience
- Strong Python skills and familiarity with async frameworks
- Experience with cloud infrastructure (AWS or GCP)
- Knowledge of distributed systems and REST API design patterns

Benefits:
- Competitive salary and meaningful equity
- Full medical, dental, and vision coverage
- 401(k) with 4% employer match
- $2,000 annual learning and development budget
- Flexible remote/hybrid schedule

Apply at careers.techcorp.com/senior-backend or email recruiting@techcorp.com`;
