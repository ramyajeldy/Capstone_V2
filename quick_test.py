from app.services.bert_service import BertEmailService

service = BertEmailService()

sample_text = """
Subject: Urgent Account Verification

Dear User,
Your account has been suspended. Click the link below to verify immediately.
"""

score = service.predict_risk(sample_text)
print("Phishing risk score:", score)


from app.services.html_parser import HTMLSuspicionService

html_service = HTMLSuspicionService()

sample_html = """
<html>
  <body>
    <h2>Urgent: Verify your account</h2>
    <form action="http://phish-login.com">
      <input type="text" name="username" />
      <input type="password" name="password" />
      <button>Login</button>
    </form>
    <a href="http://phish-login.com">www.google.com</a>
  </body>
</html>
"""

result = html_service.analyze_html(sample_html)
print(result)


from app.services.url_intelligence import URLIntelligenceService

service = URLIntelligenceService()

sample_text = """
Hello user,
Please verify your account immediately:
http://xn--pple-43d.com/login
Also visit https://www.google.com for reference.
"""

result = service.analyze_text(sample_text)
print(result)