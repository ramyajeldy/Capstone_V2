var API_BASE = 'https://phishing-api-demo-777140345679.us-central1.run.app';
var UI_VERSION = 'v1.0';

// ── Entry point: fires when user opens an email ───────────────────────────────

function onGmailMessageOpen(e) {
  var emailData = getCurrentEmailData_(e);

  return buildPreviewCard(emailData);
}

// ── Homepage card (add-on opened outside an email) ───────────────────────────

function onHomepage() {
  var card = CardService.newCardBuilder()
    .setHeader(
      CardService.newCardHeader()
        .setTitle('CyberSecure AI')
        .setSubtitle('Open an email to analyze it • ' + UI_VERSION)
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

function buildPreviewCard(emailData) {
  var analyzeAction = CardService.newAction()
    .setFunctionName('analyzeCurrentEmail')
    .setParameters({
      messageId: emailData.messageId || ''
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
        .setContent(emailData.subject || '(no subject)')
    )
    .addWidget(
      CardService.newKeyValue()
        .setTopLabel('From')
        .setContent(emailData.sender || '(unknown sender)')
    )
    .addWidget(
      CardService.newTextParagraph().setText('<b>UI Version:</b> ' + UI_VERSION)
    )
    .addWidget(CardService.newButtonSet().addButton(analyzeBtn));

  return CardService.newCardBuilder()
    .setHeader(
      CardService.newCardHeader()
        .setTitle('CyberSecure AI')
        .setSubtitle('Phishing Detector • ' + UI_VERSION)
        .setImageUrl('https://www.gstatic.com/images/branding/product/1x/gmail_2020q4_48dp.png')
    )
    .addSection(section)
    .build();
}

// ── Analyze button click: calls backend and shows result ─────────────────────

function analyzeCurrentEmail(e) {
  var params  = e.parameters;
  var messageId = params.messageId || '';
  var emailData = getCurrentEmailData_(e, messageId);

  var payloadObject = {
    subject:   emailData.subject,
    sender:    emailData.sender,
    body_text: emailData.bodyText,
    html_text: emailData.htmlText
  };
  var payload = JSON.stringify(payloadObject);

  Logger.log('CyberSecure payload summary: %s', JSON.stringify({
    subjectLength: (emailData.subject || '').length,
    senderLength: (emailData.sender || '').length,
    bodyTextLength: (emailData.bodyText || '').length,
    htmlTextLength: (emailData.htmlText || '').length
  }));

  var options = {
    method:          'POST',
    contentType:     'application/json',
    payload:         payload,
    muteHttpExceptions: true
  };

  try {
    var response = UrlFetchApp.fetch(API_BASE + '/analyze', options);
    var data     = JSON.parse(response.getContentText());

    if (response.getResponseCode() >= 400) {
      throw new Error(data.message || data.error || response.getContentText());
    }

    return CardService.newActionResponseBuilder()
      .setNavigation(
        CardService.newNavigation().pushCard(buildResultCard(data, emailData.subject, emailData.sender))
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

function getCurrentEmailData_(e, fallbackMessageId) {
  var gmailData = e.gmail || {};
  var messageId = gmailData.messageId || fallbackMessageId || '';
  var accessToken = gmailData.accessToken || '';

  if (accessToken) {
    GmailApp.setCurrentMessageAccessToken(accessToken);
  }

  if (!messageId) {
    throw new Error('Could not determine the current Gmail message.');
  }

  var message = GmailApp.getMessageById(messageId);

  return {
    messageId: messageId,
    subject: message.getSubject() || '',
    sender: message.getFrom() || '',
    bodyText: message.getPlainBody() || '',
    htmlText: message.getBody() || ''
  };
}

// ── Result card ───────────────────────────────────────────────────────────────

function buildResultCard(data, subject, sender) {
  var debug = data.debug || {};
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

  var debugLines = [
    'Subject length: ' + (debug.subject_length || 0),
    'Sender length: ' + (debug.sender_length || 0),
    'Body length: ' + (debug.body_text_length || 0),
    'HTML length: ' + (debug.html_text_length || 0),
    'Combined text length: ' + (debug.combined_text_length || 0),
    'Extracted URL count: ' + (debug.extracted_url_count || 0)
  ];

  if (debug.extracted_urls && debug.extracted_urls.length > 0) {
    debugLines.push('URLs: ' + debug.extracted_urls.join(', '));
  }

  var debugSection = CardService.newCardSection()
    .setHeader('Debug Input Summary')
    .addWidget(
      CardService.newTextParagraph().setText(debugLines.join('\n'))
    );

  // ── Stay Safe tips (high risk only) ──
  var card = CardService.newCardBuilder()
    .setHeader(
      CardService.newCardHeader()
        .setTitle('Analysis Result')
        .setSubtitle((subject || '(no subject)') + ' • ' + UI_VERSION)
        .setImageUrl('https://www.gstatic.com/images/branding/product/1x/gmail_2020q4_48dp.png')
    )
    .addSection(summarySection)
    .addSection(scoresSection)
    .addSection(reasonsSection)
    .addSection(debugSection);

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
        .setSubtitle('Could not reach the API • ' + UI_VERSION)
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
