import json
import os
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '8001'))

AUTHORIZATION_KEY = os.getenv('AUTHORIZATION_KEY', '')

BAD_WORDS = ['бляд', 'сука', 'хер', 'пизд', 'еб', 'нах', 'мраз', 'долбо', 'fuck', 'shit']


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
        return False
    auth = headers.get('Authorization', '').strip()
    if not auth:
        return False
    token = auth.replace('Bearer ', '', 1).strip() if auth.lower().startswith('bearer ') else auth
    expected = AUTHORIZATION_KEY.replace('Bearer ', '', 1).strip()
    return token == expected



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

        return self._send_json(200, {'reply': _fallback_reply(message), 'source': 'local-fallback'})


if __name__ == '__main__':
    if not AUTHORIZATION_KEY:
        raise RuntimeError('Set AUTHORIZATION_KEY in environment before starting server.')
    print(f'AI backend: http://{HOST}:{PORT}')
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
