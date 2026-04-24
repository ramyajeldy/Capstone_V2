# CyberSecure AI — Phishing & Fraud Detection Platform

An end-to-end AI-powered cybersecurity platform that detects phishing emails, malicious URLs, and fraudulent job postings using fine-tuned BERT models, URL intelligence, and HTML analysis. Includes a Gmail Add-on for in-inbox analysis and a React web dashboard.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [System Components](#system-components)
- [End-to-End Flow](#end-to-end-flow)
- [AI Models](#ai-models)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Local Setup](#local-setup)
- [Gmail Add-on Setup](#gmail-add-on-setup)
- [Deployment](#deployment)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACES                          │
│                                                                 │
│   ┌──────────────────────┐     ┌──────────────────────────┐    │
│   │   React Web App      │     │    Gmail Add-on          │    │
│   │   (Vite + TypeScript)│     │    (Google Apps Script)  │    │
│   │   localhost:5175     │     │    Gmail Sidebar         │    │
│   └──────────┬───────────┘     └────────────┬─────────────┘    │
│              │ Vite Proxy (/api)             │ UrlFetchApp      │
└──────────────┼───────────────────────────────┼──────────────────┘
               │                               │
               ▼                               ▼
┌─────────────────────────────────────────────────────────────────┐
│              FastAPI Backend — Google Cloud Run                  │
│    https://phishing-api-demo-777140345679.us-central1.run.app   │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐   │
│  │  /analyze   │  │ /analyze-jd │  │   /analyze-image     │   │
│  │  /check-url │  │             │  │   /ocr               │   │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬───────────┘   │
│         │                │                     │               │
└─────────┼────────────────┼─────────────────────┼───────────────┘
          │                │                     │
          ▼                ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                        AI / ML SERVICES                         │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐   │
│  │ BERT Phish  │  │ BERT Jobs   │  │  URL Intelligence    │   │
│  │ Detector    │  │ Detector    │  │  (BERT + WHOIS +     │   │
│  │             │  │             │  │   OpenPhish)         │   │
│  └─────────────┘  └─────────────┘  └──────────────────────┘   │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐                             │
│  │ HTML Parser │  │ Tesseract   │                             │
│  │(BeautifulSoup)│ OCR Engine  │                             │
│  └─────────────┘  └─────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## System Components

### 1. React Web Dashboard (`/frontend`)

Built with **React 18**, **Vite**, and **TypeScript**. Provides four analysis tabs:

| Tab | Endpoint Used | Description |
|---|---|---|
| Analyze Email | `POST /analyze` | Paste or receive email from Gmail add-on for phishing analysis |
| Job Scam Detector | `POST /analyze-jd` | Detect fake job postings using fine-tuned BERT |
| URL Checker | `POST /analyze` (URL as body) | Check any URL against the phishing intelligence engine |
| Phishing Awareness | — | Educational content on recognising phishing attacks |

All API calls route through a **Vite dev proxy** (`/api → Cloud Run`), eliminating CORS issues without requiring server-side CORS configuration.

### 2. FastAPI Backend (`/app`)

Python **FastAPI** service deployed on **Google Cloud Run**. Stateless, containerised, auto-scaling. Orchestrates all AI services and returns structured JSON responses.

### 3. Gmail Add-on (`/gmail_addon`)

**Google Apps Script** sidebar that activates when a user opens an email in Gmail. Reads the email's subject, sender, and body using the Gmail API, then calls the Cloud Run backend directly via `UrlFetchApp` and renders a full risk card inside Gmail — no browser tab switching required.

### 4. AI Models (`/models`)

Three fine-tuned models stored locally and served from the container:

| Model | Directory | Task |
|---|---|---|
| Phishing BERT | `models/phishing_bert_final` | Classify email text as phishing or legitimate |
| URL Intelligence | `models/bert_url_model` | Score URLs for phishing likelihood |
| Job Fraud BERT | `models/jobs_detector_model` | Detect fake job postings |

---

## End-to-End Flow

### Email Phishing Analysis

```
User pastes email (or Gmail Add-on sends it via URL params)
        │
        ▼
Frontend — GmailAnalyzerPage
  └─ POST /api/analyze → Vite proxy → Cloud Run /analyze
        │
        ▼
FastAPI: analyze() in main.py
  └─ decode_attachments()          — base64 decode any image attachments
  └─ extract_ocr_from_attachments() — Tesseract OCR on images
        │
        ▼
email_analyzer.analyze_email()
  │
  ├─ build_combined_email_text()
  │     └─ Concatenates: subject + sender + body + html + ocr_text
  │     └─ clean_text(): lowercase → replace URLs → strip noise chars
  │
  ├─ get_bert_score(combined_text)
  │     └─ Tokenise (max 256 tokens)
  │     └─ BERT forward pass → softmax → phishing probability [0–1]
  │
  ├─ analyze_urls(body + html + ocr)
  │     └─ extract_urls(): regex finds all http:// and www. links
  │     └─ Per URL:
  │           BERT URL model score
  │           WHOIS domain age lookup
  │           OpenPhish blocklist check
  │           Punycode / confusable character detection
  │     └─ Returns max_url_score + per-URL prediction + reasons
  │
  ├─ get_html_score(html_text or body_text if it contains HTML tags)
  │     └─ BeautifulSoup parse
  │     └─ Signals checked:
  │           Form elements present
  │           Password input fields
  │           JavaScript <script> tags
  │           Hidden CSS elements
  │           Suspicious keywords (verify, urgent, suspend, password…)
  │           Anchor text vs href destination mismatch
  │
  └─ calculate_risk_score()
        └─ final = (0.35 × bert) + (0.40 × url) + (0.25 × html)
        └─ Override rules applied in order:
             url_score  ≥ 0.6  →  HIGH RISK  (floor 0.75)
             url_score  ≥ 0.4  →  MEDIUM RISK (floor 0.50)
             bert_score ≥ 0.5  →  HIGH RISK  (floor 0.70)
             bert_score ≥ 0.35 →  MEDIUM RISK (floor 0.45)
             html_score ≥ 0.5  →  HIGH RISK  (floor 0.70)
        │
        ▼
Response JSON → Frontend ResultCard
  ├─ Risk label:  HIGH / MEDIUM / LOW  with colour-coded badge
  ├─ Score bars:  BERT · URL · HTML
  ├─ HTML signals list
  └─ URL breakdown with per-URL hostname, prediction, and risk %
```

### Job Fraud Detection

```
User pastes job description
        │
        ▼
Frontend — JobDetectorPage
  └─ POST /api/analyze-jd
        │
        ▼
FastAPI → analyze_job_text()
  └─ Tokenise text (max 256 tokens, padded)
  └─ BERT forward pass → softmax([legitimate_prob, fraud_prob])
  └─ fraud_probability ≥ 0.35  →  is_fake_job = True
        │
        ▼
Response: fraud_probability · legitimate_probability · confidence · label
Frontend renders probability bars and verdict card
```

### URL Check

```
User enters a URL
        │
        ▼
Frontend — UrlCheckerPage
  └─ POST /api/analyze  { body_text: "<the URL>" }
        │
        ▼
URL intelligence pipeline (same engine as email flow)
  └─ extract_urls() finds the URL in body_text
  └─ BERT URL model scores it (transformer_probability)
  └─ WHOIS lookup: domain registration age
  └─ OpenPhish blocklist: exact + domain match
  └─ Feature flags: punycode, IDN, non-ASCII host, confusable chars
        │
        ▼
Frontend extracts url_score + urls[] from response
  └─ Renders UrlResultCard: risk %, prediction, hostname, reasons
```

### Gmail Add-on Flow

```
User opens email in Gmail
        │
        ▼
Apps Script: onGmailMessageOpen(e)
  └─ GmailApp.setCurrentMessageAccessToken(accessToken)
  └─ GmailApp.getMessageById() → subject, sender, plainBody
  └─ buildPreviewCard() — renders sidebar card with:
       Subject preview
       Sender preview
       "Analyze This Email" button
        │
User clicks the button
        │
        ▼
Apps Script: analyzeCurrentEmail(e)
  └─ UrlFetchApp.fetch(Cloud Run /analyze, {
       method: POST,
       contentType: application/json,
       payload: { subject, sender, body_text, html_text: "" }
     })
  └─ JSON.parse(response.getContentText())
  └─ buildResultCard() renders:
       ⛔ HIGH / ⚠️ MEDIUM / ✅ LOW header
       ASCII progress bars  ▓▓▓▓▓░░░░░  risk score
       Score breakdown: BERT · URL · HTML
       Risk indicators list
       Stay Safe tips (high risk only)
```

---

## AI Models

### Phishing Email BERT (`phishing_bert_final`)

- **Base model**: `bert-base-uncased`
- **Task**: Binary sequence classification — phishing vs legitimate
- **Input**: Cleaned combined email text (subject + sender + body + HTML + OCR)
- **Max tokens**: 256
- **Output**: Phishing probability score (0–1)
- **Inference**: CPU (float32), no GPU required

### URL Intelligence BERT (`bert_url_model`)

- **Base model**: BERT fine-tuned on phishing URL datasets
- **Features combined**:
  - Transformer probability from BERT
  - WHOIS domain age (negative = not found)
  - OpenPhish blocklist (exact and domain-level)
  - Punycode / IDN encoding detection
  - Confusable / mixed-script hostname detection
- **Output**: `final_probability` per URL, prediction label, reasoning list

### Job Fraud BERT (`jobs_detector_model`)

- **Base model**: BERT fine-tuned on employment scam datasets
- **Task**: Binary classification — legitimate_job vs fake_job
- **Threshold**: `fraud_probability ≥ 0.35` → flagged as fake
- **Output**: `fraud_probability`, `legitimate_probability`, `confidence`, `model_name`

### Risk Score Formula

```
final_score = (0.35 × bert_score) + (0.40 × url_score) + (0.25 × html_score)

Thresholds:
  ≥ 0.7  →  HIGH RISK
  ≥ 0.4  →  MEDIUM RISK
  < 0.4  →  LOW RISK

URL analysis carries the highest weight (40%) as it is the most reliable signal.
```

---

## API Reference

**Base URL:** `https://phishing-api-demo-777140345679.us-central1.run.app`  
**Interactive docs (Swagger UI):** `/docs`

### `POST /analyze` — Email Phishing Analysis

```json
Request:
{
  "subject": "Urgent: Verify your account",
  "sender": "security@paypa1.com",
  "body_text": "Click here to verify your PayPal account or it will be suspended...",
  "html_text": "<html>...</html>",
  "attachments": []
}

Response:
{
  "risk_score": 0.75,
  "label": "high_risk",
  "confidence": 0.98,
  "bert_score": 0.41,
  "url_score": 0.9998,
  "html_score": 0.0,
  "html_signals": [],
  "url_reasons": ["Multiple suspicious phishing-related keywords found"],
  "urls": [{
    "url": "http://paypa1-verify.tk/login",
    "hostname": "paypa1-verify.tk",
    "final_probability": 0.9998,
    "prediction": "phishing",
    "reasons": ["Multiple suspicious phishing-related keywords found"]
  }],
  "latency_ms": 240.5
}
```

### `POST /analyze-jd` — Job Fraud Detection

```json
Request:
{ "text": "Work from home, earn $5000 weekly, no experience needed..." }

Response:
{
  "label": "fake_job",
  "is_fake_job": true,
  "fraud_probability": 0.9994,
  "legitimate_probability": 0.0006,
  "confidence": 0.9994,
  "threshold_used": 0.35,
  "model_name": "jobs_detector_model"
}
```

### `POST /analyze-image` — Screenshot / Image Analysis

- **Content-Type:** `multipart/form-data`
- **Field:** `file` (PNG, JPG, WebP — max 10 MB)
- Tesseract extracts text from the image, then runs the full phishing pipeline
- Response includes `ocr_text`, `source: "image_ocr"`, and all analysis fields

### `POST /ocr` — Text Extraction Only

- **Content-Type:** `multipart/form-data`
- Returns `{ text, char_count, filename }` without running phishing analysis

### `GET /health`

```json
{ "status": "ok", "services": ["phishing_detection", "job_detection", "ocr"] }
```

---

## Project Structure

```
capstone-2/
│
├── app/                               # FastAPI backend
│   ├── main.py                        # Routes, CORS, request/response models
│   ├── services/
│   │   ├── email_analyzer.py          # Orchestrates BERT + URL + HTML pipeline
│   │   ├── bert_service.py            # Phishing BERT inference
│   │   ├── url_intelligence_service.py # URL risk scoring
│   │   ├── html_parser.py             # BeautifulSoup HTML signal extraction
│   │   ├── job_detector_service.py    # Job fraud BERT inference
│   │   ├── ocr_service.py             # Tesseract OCR (file + attachment)
│   │   └── risk_engine.py             # Weighted score aggregation formula
│   └── utils/
│       ├── text_cleaner.py            # Email text normalisation + cleaning
│       └── url_extractor.py           # Regex-based URL extraction
│
├── models/                            # Fine-tuned model weights (not in git LFS)
│   ├── phishing_bert_final/           # Email phishing classifier
│   ├── bert_url_model/                # URL intelligence model
│   └── jobs_detector_model/           # Job fraud classifier
│
├── frontend/                          # React + Vite + TypeScript web app
│   ├── src/
│   │   ├── api/client.ts              # All backend API calls + type-safe wrappers
│   │   ├── types/api.ts               # TypeScript interfaces matching backend JSON
│   │   ├── pages/
│   │   │   ├── GmailAnalyzerPage.tsx  # Email analysis tab (reads URL params from add-on)
│   │   │   ├── JobDetectorPage.tsx    # Job fraud detection tab
│   │   │   ├── UrlCheckerPage.tsx     # URL checker tab
│   │   │   └── EducationPage.tsx      # Phishing awareness tab
│   │   ├── components/
│   │   │   ├── ResultCard.tsx         # Email analysis result display
│   │   │   ├── UrlList.tsx            # URL breakdown with risk % and reasons
│   │   │   ├── ScoreBadge.tsx         # HIGH / MEDIUM / LOW risk badge
│   │   │   ├── LoadingSpinner.tsx     # Loading state component
│   │   │   └── JsonViewer.tsx         # Collapsible raw API response viewer
│   │   └── index.css                  # Full UI theme (light professional)
│   ├── vite.config.ts                 # Proxy: /api/* → Cloud Run (bypasses CORS)
│   └── .env.local                     # VITE_API_URL=/api
│
└── gmail_addon/                       # Google Apps Script add-on
    ├── Code.js                        # Full add-on: preview card + analysis + result card
    ├── appsscript.json                # OAuth scopes, contextual triggers, branding
    └── DEPLOY.md                      # Step-by-step deployment guide
```

---

## Local Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Tesseract OCR — [Windows installer](https://github.com/UB-Mannheim/tesseract/wiki) | `brew install tesseract` (macOS)
- Model weights in `models/` directory

### Backend

```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Start development server
uvicorn app.main:app --reload
# API running at  → http://localhost:8000
# Swagger docs at → http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

By default the frontend proxies all `/api` requests to Cloud Run via `.env.local`.  
To switch to your local backend:

```bash
# frontend/.env.local
VITE_API_URL=http://localhost:8000
```

---

## Gmail Add-on Setup

1. Go to [script.google.com](https://script.google.com) → **New project**
2. Rename it to **CyberSecure AI — Phishing Detector**
3. Paste the contents of `gmail_addon/Code.js` into `Code.gs`
4. Open **Project Settings → Show `appsscript.json` manifest** → paste `gmail_addon/appsscript.json`
5. Click **Run → `onHomepage`** → authorise the requested OAuth scopes
6. **Deploy → New deployment → Type: Gmail Add-on** → copy the Deployment ID
7. In Gmail: **Extensions → Manage add-ons** → find your add-on → Install

Once installed, open any email in Gmail. The sidebar shows a preview card with an **Analyze This Email** button. Clicking it calls the Cloud Run backend and renders the full risk assessment — including score bars, risk indicators, and Stay Safe tips — without leaving Gmail.

---

## Deployment

The backend is packaged as a Docker container and deployed to **Google Cloud Run**.

```bash
# Build and push the container image
gcloud builds submit --tag gcr.io/PROJECT_ID/cybersecure-ai

# Deploy to Cloud Run
gcloud run deploy cybersecure-ai \
  --image gcr.io/PROJECT_ID/cybersecure-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi
```

| Resource | URL |
|---|---|
| Live API | `https://phishing-api-demo-777140345679.us-central1.run.app` |
| Swagger Docs | `https://phishing-api-demo-777140345679.us-central1.run.app/docs` |
| Health Check | `https://phishing-api-demo-777140345679.us-central1.run.app/health` |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite 5, TypeScript |
| Backend | Python 3.11, FastAPI, Uvicorn |
| ML Framework | PyTorch, HuggingFace Transformers |
| OCR Engine | Tesseract via pytesseract, Pillow |
| HTML Parsing | BeautifulSoup4 |
| Gmail Integration | Google Apps Script (V8 runtime) |
| Deployment | Google Cloud Run (auto-scaling, serverless) |
| Dev Proxy | Vite server proxy — eliminates CORS in development |
