import re

URL_REGEX = r'https?://[^\s<>"\']+|www\.[^\s<>"\']+'

def extract_urls(text: str) -> list[str]:
    if not text:
        return []

    urls = re.findall(URL_REGEX, text)
    seen = set()
    unique_urls = []

    for url in urls:
        cleaned = url.strip().rstrip(".,);]")
        if cleaned not in seen:
            seen.add(cleaned)
            unique_urls.append(cleaned)

    return unique_urls