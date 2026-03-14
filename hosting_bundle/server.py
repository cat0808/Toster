import json
import os
import uuid
import base64
from urllib import request, parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '8001'))

GIGACHAT_CLIENT_ID = os.getenv('GIGACHAT_CLIENT_ID', '')
GIGACHAT_CLIENT_SECRET = os.getenv('GIGACHAT_CLIENT_SECRET', '')
GIGACHAT_SCOPE = os.getenv('GIGACHAT_SCOPE', 'GIGACHAT_API_PERS')
GIGACHAT_MODEL = os.getenv('GIGACHAT_MODEL', 'GigaChat')
GIGACHAT_AUTH_URL = os.getenv('GIGACHAT_AUTH_URL', 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth')
GIGACHAT_API_URL = os.getenv('GIGACHAT_API_URL', 'https://gigachat.devices.sberbank.ru/api/v1/chat/completions')
AUTHORIZATION_KEY = os.getenv('AUTHORIZATION_KEY', '')

BAD_WORDS = ['бляд', 'сука', 'хер', 'пизд', 'еб', 'нах', 'мраз', 'долбо', 'fuck', 'shit']
TOKEN = {'value': None, 'exp': 0}


def _json_bytes(data):
    return json.dumps(data, ensure_ascii=False).encode('utf-8')


def _contains_bad_words(text: str) -> bool:
    low = text.lower()
    return any(word in low for word in BAD_WORDS)


def _fallback_reply(msg: str) -> str:
    t = msg.lower()
    if 'трев' in t or 'страш' in t:
        return 'Понимаю, что сейчас тревожно. Попробуй дыхание 4-4-4: вдох 4 сек, выдох 4 сек, 4 раза.'
    if 'ссор' in t or 'конфликт' in t:
        return 'Конфликты тяжело переживаются. Попробуй сказать: «Мне неприятно, когда...». Могу помочь подобрать слова.'
    return 'Я рядом и готов поддержать. Расскажи, что произошло и что ты сейчас чувствуешь.'


def _is_authorized(headers) -> bool:
    if not AUTHORIZATION_KEY:
        return True
    auth = headers.get('Authorization', '').strip()
    if not auth:
        return False
    token = auth.replace('Bearer ', '', 1).strip() if auth.lower().startswith('bearer ') else auth
    expected = AUTHORIZATION_KEY.replace('Bearer ', '', 1).strip()
    return token == expected


def _fetch_token():
    if not GIGACHAT_CLIENT_ID or not GIGACHAT_CLIENT_SECRET:
        raise RuntimeError('No GigaChat credentials')

    import time
    if TOKEN['value'] and time.time() < TOKEN['exp'] - 30:
        return TOKEN['value']

    basic = base64.b64encode(f'{GIGACHAT_CLIENT_ID}:{GIGACHAT_CLIENT_SECRET}'.encode()).decode()
    body = parse.urlencode({'scope': GIGACHAT_SCOPE}).encode()
    req = request.Request(
        GIGACHAT_AUTH_URL,
        data=body,
        method='POST',
        headers={
            'Authorization': f'Basic {basic}',
            'RqUID': str(uuid.uuid4()),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    )
    with request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode())
    TOKEN['value'] = data['access_token']
    TOKEN['exp'] = time.time() + int(data.get('expires_in', 1800))
    return TOKEN['value']


def _ask_gigachat(message: str) -> str:
    token = _fetch_token()
    payload = {
        'model': GIGACHAT_MODEL,
        'temperature': 0.7,
        'messages': [
            {'role': 'system', 'content': 'Ты доброжелательный школьный психолог. Отвечай кратко и поддерживающе.'},
            {'role': 'user', 'content': message},
        ],
    }
    req = request.Request(
        GIGACHAT_API_URL,
        data=_json_bytes(payload),
        method='POST',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
    )
    with request.urlopen(req, timeout=25) as resp:
        data = json.loads(resp.read().decode())
    return data.get('choices', [{}])[0].get('message', {}).get('content', 'Я рядом и готов помочь.')


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, code, data):
        body = _json_bytes(data)
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_POST(self):
        if self.path != '/api/chat':
            return self._send_json(404, {'error': 'Not found'})

        if not _is_authorized(self.headers):
            return self._send_json(401, {'error': 'Unauthorized. Invalid Authorization Key.'})

        length = int(self.headers.get('Content-Length', '0'))
        raw = self.rfile.read(length) if length else b'{}'
        body = json.loads(raw.decode('utf-8'))
        message = str(body.get('message', '')).strip()

        if not message:
            return self._send_json(400, {'error': 'Введите сообщение.'})
        if _contains_bad_words(message):
            return self._send_json(200, {'reply': 'Пожалуйста, переформулируй без грубых слов 💙'})

        try:
            if GIGACHAT_CLIENT_ID and GIGACHAT_CLIENT_SECRET:
                return self._send_json(200, {'reply': _ask_gigachat(message), 'source': 'gigachat'})
            return self._send_json(200, {'reply': _fallback_reply(message), 'source': 'local-fallback'})
        except Exception as e:
            return self._send_json(200, {'reply': _fallback_reply(message), 'source': 'local-fallback', 'note': f'gigachat_error: {e}'})


if __name__ == '__main__':
    print(f'AI backend: http://{HOST}:{PORT}')
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
