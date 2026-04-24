import re

URL_REGEX = r'https?://[^\s<>"\']+|www\.[^\s<>"\']+'
DOMAIN_REGEX = r'(?<!@)\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b'
EMAIL_REGEX = r'\b[a-zA-Z0-9._%+-]+@((?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,})\b'
IGNORED_DOMAIN_SUFFIXES = {
    "png",
    "jpg",
    "jpeg",
    "gif",
    "webp",
    "svg",
    "pdf",
    "txt",
    "html",
    "css",
    "js",
}

def extract_urls(text: str) -> list[str]:
    if not text:
        return []

    urls = re.findall(URL_REGEX, text)
    bare_domains = re.findall(DOMAIN_REGEX, text)
    email_domains = re.findall(EMAIL_REGEX, text)

    seen = set()
    unique_urls = []

    for url in [*urls, *bare_domains, *email_domains]:
        cleaned = url.strip().rstrip(".,);]")
        if "." not in cleaned:
            continue

        suffix = cleaned.rsplit(".", 1)[-1].lower()
        if suffix in IGNORED_DOMAIN_SUFFIXES:
            continue

        if cleaned not in seen:
            seen.add(cleaned)
            unique_urls.append(cleaned)

    return unique_urls
