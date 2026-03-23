from flask import Flask, render_template_string, jsonify, request
import json
import requests
from datetime import datetime

app = Flask(__name__)

MESSAGES_FILE = '/home/jmaudisio/dashboard/messages.json'
TELEGRAM_BOT_TOKEN = '8687530263:AAHD9ZVHb5hPIfrucuSbngw1vgT3vcFArQw'

def load_messages():
    try:
        with open(MESSAGES_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_messages(msgs):
    with open(MESSAGES_FILE, 'w') as f:
        json.dump(msgs, f, indent=2)

HTML = open('/Users/jmaudisio/.openclaw/workspace/dashboard-template.html').read()

def get_stats(messages):
    stats = {'cycling': 0, 'ai': 0, 'ios': 0, 'gaming': 0}
    for msg in messages:
        cat = msg.get('category', '').lower()
        if 'cycling' in cat: stats['cycling'] += 1
        elif 'ai' in cat or 'ia' in cat: stats['ai'] += 1
        elif 'ios' in cat or 'swift' in cat: stats['ios'] += 1
        elif 'gaming' in cat or 'game' in cat: stats['gaming'] += 1
    return stats

@app.route('/')
def index():
    messages = load_messages()
    stats = get_stats(messages)
    return render_template_string(HTML, messages=messages, stats=stats)

@app.route('/api/messages', methods=['POST'])
def save_message():
    data = request.get_json() or request.form
    msg = {
        'title': data.get('title'),
        'category': data.get('category', 'default'),
        'content': data.get('content', ''),
        'created_at': datetime.now().isoformat()
    }
    messages = load_messages()
    messages.append(msg)
    save_messages(messages)
    return {'success': True}

@app.route('/api/messages', methods=['GET'])
def get_messages():
    return jsonify(load_messages())

@app.route('/api/telegram/send', methods=['POST'])
def send_telegram():
    data = request.get_json()
    text = data.get('text', '')
    
    try:
        url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
        payload = {'chat_id': 5640773790, 'text': text, 'parse_mode': 'Markdown'}
        r = requests.post(url, json=payload, timeout=10)
        return r.json()
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.route('/api/telegram/webhook', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
        response = "✅ Mensaje recibido! Usa /status para ver el dashboard."
        requests.post(url, json={'chat_id': chat_id, 'text': response, 'parse_mode': 'Markdown'})
    return 'ok'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
