# Gmail Add-on — Deployment Guide

## One-time setup

### 1. Create the Apps Script project

1. Go to https://script.google.com → **New project**
2. Name it **CyberSecure AI — Phishing Detector**

### 2. Copy the files

In the Apps Script editor:

| File to create | Source file |
|---|---|
| `Code.gs` (rename default `Code.gs`) | Copy contents of `Code.js` |
| `appsscript.json` | Project Settings → **Show "appsscript.json"** → paste contents |

### 3. Enable Advanced Services

**Services** (left sidebar) → **+** → enable **Gmail API**

### 4. Test locally

1. Click **Run** → select `onHomepage` → authorize scopes when prompted
2. Use **Test deployments** → Gmail contextual trigger to preview in Gmail

### 5. Deploy as Gmail Add-on

1. **Deploy** → **New deployment**
2. Type: **Gmail Add-on**
3. Description: `v1 — BERT phishing detection`
4. Click **Deploy** → copy the **Deployment ID**

### 6. Install for yourself (tester install)

`Extensions` menu in Gmail → **Manage add-ons** → find your add-on → Install

OR use the Deployment ID:

1. Gmail → right sidebar gear → **Get add-ons**
2. Click your add-on tile → Install

---

## How it works (demo flow)

1. Open any email in Gmail
2. The add-on sidebar shows **subject + sender preview**
3. Click **🔍 Analyze This Email**
4. Results card shows:
   - Color-coded header: ⛔ HIGH RISK / ⚠️ MEDIUM RISK / ✅ LOW RISK
   - Risk score + confidence score bars (▓▓▓▓▓▓░░░░)
   - Component scores: BERT / URL Intelligence / HTML Structure
   - Expandable: HTML signals, URL analysis, Stay Safe tips

---

## API endpoint

`POST https://phishing-api-demo-777140345679.us-central1.run.app/analyze`

Payload:
```json
{
  "subject": "...",
  "sender": "...",
  "body_text": "...",
  "html_text": "..."
}
```

---

## Scopes required

| Scope | Purpose |
|---|---|
| `gmail.addons.execute` | Run the add-on |
| `gmail.addons.current.message.readonly` | Read open email |
| `script.external_request` | Call the phishing API |
