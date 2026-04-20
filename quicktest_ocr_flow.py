from app.services.email_analyzer import analyze_email

with open(r"C:\Users\Ramya\Downloads\ocr-test.png", "rb") as f:
    image_bytes = f.read()

attachments = [
    {
        "filename": "phishing.png",
        "content_type": "image/png",
        "data": image_bytes
    }
]

result = analyze_email(
    subject="Invoice Notice",
    sender="billing@unknownservice.com",
    body_text="Please check attached invoice",
    html_text="",
    attachments=attachments
)

print(result)