#!/bin/bash
# Token report email script

# Get current timestamp for email
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Get token status and extract only token lines
TOKENS=$(/opt/homebrew/bin/openclaw status 2>/dev/null | grep -E "k/200k|k/128k" | head -5)

# Send email via Resend
curl -s -X POST "https://api.resend.com/emails" \
  -H "Authorization: Bearer e_BNZqQcAu_CXy8q5qscoZ8XcwoehfVdZfx" \
  -H "Content-Type: application/json" \
  -d @- <<EOF
{
  "from": "Aria Agent <aria.agent@saraiba.eu>",
  "to": ["aspontes@saraiba.eu"],
  "subject": "📊 Token Report - $TIMESTAMP",
  "text": "📊 INFORME DE TOKENS - $TIMESTAMP\n\n$TOKENS\n\nEnviado cada 6 horas."
}
EOF

echo "Email sent at $TIMESTAMP"
