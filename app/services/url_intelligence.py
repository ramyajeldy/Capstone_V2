import re
import ipaddress
from urllib.parse import urlparse, unquote
from html import unescape
from typing import List, Dict, Any

import tldextract
import idna


URL_REGEX = r"""(?i)\b((?:https?://|www\.)[^\s<>"'()]+)"""


class URLIntelligenceService:
    def __init__(self):
        self.suspicious_keywords = {
            "login", "verify", "secure", "update", "account",
            "bank", "signin", "confirm", "password", "payment",
            "suspended", "unlock", "reset", "invoice", "wallet"
        }

    def extract_urls(self, text: str) -> List[str]:
        if not text:
            return []

        text = unescape(text)
        urls = re.findall(URL_REGEX, text)

        cleaned = []
        for url in urls:
            url = url.strip().rstrip(".,);]")
            if url.startswith("www."):
                url = "http://" + url
            cleaned.append(url)

        # preserve order, remove duplicates
        seen = set()
        unique_urls = []
        for url in cleaned:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)

        return unique_urls

    def _get_host(self, url: str) -> str:
        try:
            parsed = urlparse(url)
            return (parsed.hostname or "").lower()
        except Exception:
            return ""

    def _is_ip_address(self, host: str) -> bool:
        try:
            ipaddress.ip_address(host)
            return True
        except ValueError:
            return False

    def _registered_domain(self, host: str) -> str:
        ext = tldextract.extract(host)
        if ext.domain and ext.suffix:
            return f"{ext.domain}.{ext.suffix}"
        return host

    def _has_punycode(self, host: str) -> bool:
        return "xn--" in host.lower()

    def _subdomain_count(self, host: str) -> int:
        ext = tldextract.extract(host)
        if not ext.subdomain:
            return 0
        return len([p for p in ext.subdomain.split(".") if p])

    def _has_suspicious_keywords(self, url: str) -> List[str]:
        lower_url = unquote(url).lower()
        return [kw for kw in self.suspicious_keywords if kw in lower_url]

    def _looks_obfuscated(self, url: str) -> bool:
        lower_url = url.lower()
        return any(x in lower_url for x in ["%2f", "%2e", "%40", "%25"])

    def analyze_url(self, url: str) -> Dict[str, Any]:
        score = 0.0
        reasons = []

        parsed = urlparse(url)
        host = self._get_host(url)
        registered_domain = self._registered_domain(host)

        if not host:
            return {
                "url": url,
                "registered_domain": "",
                "url_score": 0.0,
                "reasons": ["Could not parse hostname"]
            }

        # 1. Punycode
        if self._has_punycode(host):
            score += 0.30
            reasons.append("Punycode detected in hostname")

        # 2. Direct IP usage
        if self._is_ip_address(host):
            score += 0.25
            reasons.append("IP address used instead of domain")

        # 3. Too many subdomains
        sub_count = self._subdomain_count(host)
        if sub_count >= 3:
            score += 0.15
            reasons.append(f"Many subdomains detected ({sub_count})")

        # 4. Suspicious keywords
        matched_keywords = self._has_suspicious_keywords(url)
        if matched_keywords:
            score += min(0.25, 0.08 * len(matched_keywords))
            reasons.append(f"Suspicious keywords in URL: {', '.join(matched_keywords)}")

        # 5. Long URL
        if len(url) > 100:
            score += 0.10
            reasons.append("Very long URL")

        # 6. @ symbol trick
        if "@" in url:
            score += 0.20
            reasons.append("@ symbol present in URL")

        # 7. Too many hyphens in host
        hyphen_count = host.count("-")
        if hyphen_count >= 2:
            score += 0.10
            reasons.append(f"Multiple hyphens in hostname ({hyphen_count})")

        # 8. HTTP instead of HTTPS
        if parsed.scheme.lower() == "http":
            score += 0.05
            reasons.append("Uses HTTP instead of HTTPS")

        # 9. URL obfuscation / encoding
        if self._looks_obfuscated(url):
            score += 0.10
            reasons.append("Encoded or obfuscated URL pattern detected")

        # 10. Confusable non-ascii characters
        try:
            host.encode("ascii")
        except UnicodeEncodeError:
            score += 0.20
            reasons.append("Non-ASCII characters in hostname")

        score = min(round(score, 4), 1.0)

        if not reasons:
            reasons.append("No major suspicious URL indicators detected")

        return {
            "url": url,
            "registered_domain": registered_domain,
            "url_score": score,
            "reasons": reasons
        }

    def analyze_text(self, text: str) -> Dict[str, Any]:
        urls = self.extract_urls(text)

        if not urls:
            return {
                "urls_found": [],
                "url_score": 0.0,
                "top_reason": "No URLs found",
                "per_url_results": []
            }

        results = [self.analyze_url(url) for url in urls]
        top_result = max(results, key=lambda x: x["url_score"])

        return {
            "urls_found": urls,
            "url_score": top_result["url_score"],   # use max-risk URL
            "top_reason": "; ".join(top_result["reasons"]),
            "per_url_results": results
        }