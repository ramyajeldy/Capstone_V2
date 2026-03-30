from bs4 import BeautifulSoup
import re


class HTMLSuspicionService:
    def __init__(self):
        self.suspicious_terms = [
            "verify",
            "urgent",
            "login",
            "update",
            "password",
            "bank",
            "confirm",
            "suspend",
            "security alert",
            "account"
        ]

    def analyze_html(self, html: str) -> dict:
        if not html or not html.strip():
            return {
                "html_suspicion_score": 0.0,
                "signals": []
            }

        soup = BeautifulSoup(html, "html.parser")
        score = 0.0
        signals = []

        # 1. Form detected
        if soup.find("form"):
            score += 0.25
            signals.append("HTML contains a form")

        # 2. Password field detected
        password_input = soup.find("input", {"type": "password"})
        if password_input:
            score += 0.25
            signals.append("Password input field detected")

        # 3. Script tags detected
        if soup.find("script"):
            score += 0.10
            signals.append("Script tags detected")

        # 4. Hidden elements
        hidden_elements = soup.find_all(
            style=re.compile(r"display\s*:\s*none", re.I)
        )
        if hidden_elements:
            score += 0.10
            signals.append("Hidden HTML elements detected")

        # 5. Suspicious keywords in visible text
        text = soup.get_text(" ", strip=True).lower()
        matched_terms = []
        for term in self.suspicious_terms:
            if term in text:
                matched_terms.append(term)

        if matched_terms:
            score += min(0.20, 0.05 * len(matched_terms))
            signals.append(f"Suspicious terms found: {', '.join(matched_terms)}")

        # 6. Anchor text / href mismatch
        for a in soup.find_all("a", href=True):
            anchor_text = a.get_text(" ", strip=True)
            href = a["href"].strip()

            if anchor_text and href.startswith("http"):
                if anchor_text not in href and len(anchor_text) > 3:
                    score += 0.15
                    signals.append("Anchor text mismatches destination URL")
                    break

        # clamp score between 0 and 1
        score = min(score, 1.0)

        return {
            "html_suspicion_score": round(score, 4),
            "signals": signals
        }