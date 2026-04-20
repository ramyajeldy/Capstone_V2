from app.services.email_analyzer import analyze_email

print("PHISHING EMAIL")
result = analyze_email(
    subject="Urgent: Verify your account",
    sender="support@secure-bank.com",
    body_text="Please verify your account immediately using https://bit.ly/secure-login-now",
    html_text="<form><input type='password'>Enter password</form>",
    attachments=[]
)

print("Risk Score:", result["risk_score"])
print("Label:", result["label"])
print("BERT Score:", result["bert_score"])
print("URL Score:", result["url_score"])
print("HTML Score:", result["html_score"])
print("HTML Signals:", result["html_signals"])
print("URL Reasons:", result["url_reasons"])
print("Important Tokens:", result["important_tokens"])

print("\nSAFE EMAIL")
safe_result = analyze_email(
    subject="Team lunch tomorrow",
    sender="manager@google.com",
    body_text="Please join us for lunch tomorrow at 1 PM in Meeting Room A.",
    html_text="",
    attachments=[]
)

print("Risk Score:", safe_result["risk_score"])
print("Label:", safe_result["label"])
print("BERT Score:", safe_result["bert_score"])
print("URL Score:", safe_result["url_score"])
print("HTML Score:", safe_result["html_score"])
print("HTML Signals:", safe_result["html_signals"])
print("URL Reasons:", safe_result["url_reasons"])
print("Important Tokens:", safe_result["important_tokens"])

print("\nOCR-BASED PHISHING EMAIL")
ocr_demo = analyze_email(
    subject="Invoice Notice",
    sender="billing@atyourservice.com",
    body_text="",
    html_text="",
    attachments=[]
)

# temporary demo if not passing real attachment in this test:
ocr_demo_text = "Your subscription will renew today and $417.00 is about to be debited from your account. If you didn't authorize this charge, call now."