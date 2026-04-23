var API_BASE = 'https://phishing-api-demo-777140345679.us-central1.run.app';

// ── Entry point: fires when user opens an email ───────────────────────────────

function onGmailMessageOpen(e) {
  var messageId = e.gmail.messageId;
  var accessToken = e.gmail.accessToken;
  GmailApp.setCurrentMessageAccessToken(accessToken);

  var message = GmailApp.getMessageById(messageId);
  var subject = message.getSubject() || '';
  var sender  = message.getFrom()    || '';
  var body    = message.getPlainBody() || '';

  return buildPreviewCard(subject, sender, body);
}

// ── Homepage card (add-on opened outside an email) ───────────────────────────

function onHomepage() {
  var card = CardService.newCardBuilder()
    .setHeader(
      CardService.newCardHeader()
        .setTitle('CyberSecure AI')
        .setSubtitle('Open an email to analyze it')
        .setImageUrl('https://www.gstatic.com/images/branding/product/1x/gmail_2020q4_48dp.png')
    );

  var section = CardService.newCardSection()
    .addWidget(
      CardService.newTextParagraph().setText(
        '📬 Open any email in Gmail and this add-on will show a preview with an <b>Analyze</b> button.'
      )
    );

  card.addSection(section);
  return card.build();
}

// ── Preview card: shows subject + sender and the Analyze button ───────────────

function buildPreviewCard(subject, sender, body) {
  var safeBody = body.length > 4000 ? body.substring(0, 4000) : body;

  var analyzeAction = CardService.newAction()
    .setFunctionName('analyzeCurrentEmail')
    .setParameters({
      subject: subject,
      sender:  sender,
      body:    safeBody
    });

  var analyzeBtn = CardService.newTextButton()
    .setText('🔍 Analyze This Email')
    .setOnClickAction(analyzeAction)
    .setTextButtonStyle(CardService.TextButtonStyle.FILLED)
    .setBackgroundColor('#2563eb');

  var section = CardService.newCardSection()
    .setHeader('Email Preview')
    .addWidget(
      CardService.newKeyValue()
        .setTopLabel('Subject')
        .setContent(subject || '(no subject)')
    )
    .addWidget(
      CardService.newKeyValue()
        .setTopLabel('From')
        .setContent(sender || '(unknown sender)')
    )
    .addWidget(CardService.newButtonSet().addButton(analyzeBtn));

  return CardService.newCardBuilder()
    .setHeader(
      CardService.newCardHeader()
        .setTitle('CyberSecure AI')
        .setSubtitle('Phishing Detector')
        .setImageUrl('https://www.gstatic.com/images/branding/product/1x/gmail_2020q4_48dp.png')
    )
    .addSection(section)
    .build();
}

// ── Analyze button click: calls backend and shows result ─────────────────────

function analyzeCurrentEmail(e) {
  var params  = e.parameters;
  var subject = params.subject || '';
  var sender  = params.sender  || '';
  var body    = params.body    || '';

  var payload = JSON.stringify({
    subject:   subject,
    sender:    sender,
    body_text: body,
    html_text: ''
  });

  var options = {
    method:          'POST',
    contentType:     'application/json',
    payload:         payload,
    muteHttpExceptions: true
  };

  try {
    var response = UrlFetchApp.fetch(API_BASE + '/analyze', options);
    var data     = JSON.parse(response.getContentText());
    return CardService.newActionResponseBuilder()
      .setNavigation(
        CardService.newNavigation().pushCard(buildResultCard(data, subject, sender))
      )
      .build();
  } catch (err) {
    return CardService.newActionResponseBuilder()
      .setNavigation(
        CardService.newNavigation().pushCard(buildErrorCard(err.toString()))
      )
      .build();
  }
}

// ── Result card ───────────────────────────────────────────────────────────────

function buildResultCard(data, subject, sender) {
  var score     = Math.round((data.risk_score  || 0) * 100);
  var bert      = Math.round((data.bert_score  || 0) * 100);
  var urlScore  = Math.round((data.url_score   || 0) * 100);
  var htmlScore = Math.round((data.html_score  || 0) * 100);
  var label     = data.label || 'unknown';
  var confidence = Math.round((data.confidence || 0) * 100);

  var riskIcon, riskColor, riskText;
  if (label === 'high_risk') {
    riskIcon  = '⛔';
    riskColor = '#dc2626';
    riskText  = 'HIGH RISK — Likely Phishing';
  } else if (label === 'medium_risk') {
    riskIcon  = '⚠️';
    riskColor = '#d97706';
    riskText  = 'MEDIUM RISK — Suspicious';
  } else {
    riskIcon  = '✅';
    riskColor = '#059669';
    riskText  = 'LOW RISK — Likely Safe';
  }

  var scoreBar = buildBar(score);

  // ── Summary section ──
  var summarySection = CardService.newCardSection()
    .setHeader(riskIcon + ' ' + riskText)
    .addWidget(
      CardService.newKeyValue()
        .setTopLabel('Risk Score')
        .setContent(scoreBar + ' ' + score + '%')
    )
    .addWidget(
      CardService.newKeyValue()
        .setTopLabel('Confidence')
        .setContent(confidence + '%')
    );

  // ── Score breakdown section ──
  var scoresSection = CardService.newCardSection()
    .setHeader('Score Breakdown')
    .addWidget(
      CardService.newKeyValue()
        .setTopLabel('BERT Model')
        .setContent(buildBar(bert) + ' ' + bert + '%')
    )
    .addWidget(
      CardService.newKeyValue()
        .setTopLabel('URL Analysis')
        .setContent(buildBar(urlScore) + ' ' + urlScore + '%')
    )
    .addWidget(
      CardService.newKeyValue()
        .setTopLabel('HTML Analysis')
        .setContent(buildBar(htmlScore) + ' ' + htmlScore + '%')
    );

  // ── URL reasons section ──
  var reasons = data.url_reasons || [];
  var reasonsSection = CardService.newCardSection().setHeader('Risk Indicators');
  if (reasons.length > 0) {
    reasonsSection.addWidget(
      CardService.newTextParagraph().setText(reasons.map(function(r) { return '• ' + r; }).join('\n'))
    );
  } else {
    reasonsSection.addWidget(
      CardService.newTextParagraph().setText('No specific URL risk indicators detected.')
    );
  }

  // ── Stay Safe tips (high risk only) ──
  var card = CardService.newCardBuilder()
    .setHeader(
      CardService.newCardHeader()
        .setTitle('Analysis Result')
        .setSubtitle(subject || '(no subject)')
        .setImageUrl('https://www.gstatic.com/images/branding/product/1x/gmail_2020q4_48dp.png')
    )
    .addSection(summarySection)
    .addSection(scoresSection)
    .addSection(reasonsSection);

  if (label === 'high_risk') {
    var tipsSection = CardService.newCardSection()
      .setHeader('⚠️ Stay Safe')
      .addWidget(
        CardService.newTextParagraph().setText(
          '• Do not click any links in this email\n' +
          '• Do not provide personal or financial information\n' +
          '• Report the email as phishing in Gmail\n' +
          '• Verify the sender through official channels'
        )
      );
    card.addSection(tipsSection);
  }

  return card.build();
}

// ── Error card ────────────────────────────────────────────────────────────────

function buildErrorCard(message) {
  return CardService.newCardBuilder()
    .setHeader(
      CardService.newCardHeader()
        .setTitle('Analysis Failed')
        .setSubtitle('Could not reach the API')
    )
    .addSection(
      CardService.newCardSection()
        .addWidget(CardService.newTextParagraph().setText('Error: ' + message))
    )
    .build();
}

// ── Utility: ASCII progress bar ───────────────────────────────────────────────

function buildBar(pct) {
  var filled = Math.round(pct / 10);
  var empty  = 10 - filled;
  return '▓'.repeat(filled) + '░'.repeat(empty);
}
