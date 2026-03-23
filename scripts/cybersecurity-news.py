#!/usr/bin/env python3
import urllib.request
import json
import subprocess
from datetime import date

today = date.today().strftime('%d/%m/%Y')

def get_titles(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8')
        titles = []
        for line in content.split('<title>'):
            if '</title>' in line:
                title = line.split('</title>')[0].strip()
                if title and 'RSS' not in title and 'Feed' not in title:
                    titles.append(title)
        return titles[:5]
    except Exception as e:
        return [f'Error: {e}']

thn = get_titles('https://feeds.feedburner.com/TheHackersNews')
wls = get_titles('https://www.welivesecurity.com/feed/')

body = f"""RESUMEN DE CIBERSEGURIDAD - {today}

TOP NOTICIAS - The Hacker News:
"""

for i, t in enumerate(thn[:5]):
    body += f"• {t}\n"

body += """
WE LIVE SECURITY:
"""

for i, t in enumerate(wls[:5]):
    body += f"• {t}\n"

body += f"""
---
Ver todas: https://flipboard.com/@polibio/ciberseguridad-7s7knm1ky

Enviado cada día a las 6:00 AM"""

email_data = {
    "from": "Aria Agent <aria.agent@saraiba.eu>",
    "to": ["aspontes@saraiba.eu"],
    "subject": f"Resumen Ciberseguridad - {today}",
    "text": body
}

cmd = ['curl', '-s', '-X', 'POST', 'https://api.resend.com/emails',
       '-H', 'Authorization: Bearer e_BNZqQcAu_CXy8q5qscoZ8XcwoehfVdZfx',
       '-H', 'Content-Type: application/json',
       '-d', json.dumps(email_data)]

result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)
