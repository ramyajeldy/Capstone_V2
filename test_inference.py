from app.services.url_intelligence_service import analyze_urls

sample_text = """
Please verify your account:
https://bit.ly/secure-login-now

Backup:
http://paypal-secure-login.verify-user.com
"""

result = analyze_urls(sample_text)

print(result["max_url_score"])
print(result["avg_url_score"])
print(result["url_reasons"])
print(result["urls"])