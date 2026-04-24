from app.services.bert_service import get_bert_score

print(get_bert_score("verify your account immediately to avoid suspension"))

from app.services.ocr_service import extract_text_from_image_bytes

with open(r"C:\Users\Ramya\Downloads\ocr-test.png", "rb") as f:
    data = f.read()

print(extract_text_from_image_bytes(data))

from app.utils.text_cleaner import build_combined_email_text

sample = build_combined_email_text(
    subject="Urgent: Verify account",
    sender="support@secure-bank.com",
    body_text="Please verify your account immediately.",
    html_text="<form>Enter password</form>",
    ocr_text="If you did not authorize this payment call now"
)

print(sample)

from app.utils.text_cleaner import build_combined_email_text
from app.services.bert_service import get_bert_score

combined_text = build_combined_email_text(
    subject="Urgent: Verify account",
    sender="support@secure-bank.com",
    body_text="Please verify your account immediately.",
    html_text="<form>Enter password</form>",
    ocr_text="If you did not authorize this payment call now"
)

result = get_bert_score(combined_text)

print(combined_text)
print(result)


safe_text = build_combined_email_text(
    subject="Team lunch tomorrow",
    sender="manager@google.com",
    body_text="Please join us for lunch tomorrow at 1 PM in meeting room A.",
    html_text="",
    ocr_text=""
)

print(get_bert_score(safe_text))


cases = [
    "Team lunch tomorrow at 1 PM",
    "Your Amazon order has been shipped",
    "Verify your account immediately to avoid suspension"
]

for text in cases:
    print(text)
    print(get_bert_score(text))
    print("------")


from app.utils.url_extractor import extract_urls

sample_text = """
Please verify your account:
https://secure-login-example.com/reset

Backup:
www.boka-bank-alert.com/verify

Another copy:
https://secure-login-example.com/reset
"""

print(extract_urls(sample_text))


from app.services.url_intelligence_service import analyze_urls

sample_text = """
Please verify your account:
https://secure-login-example.com/reset

Backup:
www.boka-bank-alert.com/verify
"""

result = analyze_urls(sample_text)
print(result["max_url_score"])
print(result["avg_url_score"])
print(result["url_reasons"])
print(len(result["urls"]))


from app.services.explainability_service import explain_text

sample = """
subject urgent verify account sender support secure-bank.com
ocr_extracted_text if you did not authorize this payment call now
body_text please verify your account immediately
html_text <form>enter password</form>
"""

print(explain_text(sample, top_k=10))