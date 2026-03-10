import json
import os
import re
import uuid
import base64
from pathlib import Path
from urllib import request, parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

ROOT = Path(__file__).resolve().parent
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '3000'))

GIGACHAT_CLIENT_ID = os.getenv('GIGACHAT_CLIENT_ID', '')
GIGACHAT_CLIENT_SECRET = os.getenv('GIGACHAT_CLIENT_SECRET', '')
GIGACHAT_SCOPE = os.getenv('GIGACHAT_SCOPE', 'GIGACHAT_API_PERS')
GIGACHAT_MODEL = os.getenv('GIGACHAT_MODEL', 'GigaChat')
GIGACHAT_AUTH_URL = os.getenv('GIGACHAT_AUTH_URL', 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth')
GIGACHAT_API_URL = os.getenv('GIGACHAT_API_URL', 'https://gigachat.devices.sberbank.ru/api/v1/chat/completions')

BAD_WORDS = ['бляд', 'сука', 'хер', 'пизд', 'еб', 'нах', 'мраз', 'долбо', 'fuck', 'shit']

MUSIC_EXTS = {'.mp3', '.wav', '.ogg', '.m4a'}
PHOTO_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}

STATIC_FILES = {
    '/': 'index.html',
    '/index.html': 'index.html',
    '/app.js': 'app.js',
    '/styles.css': 'styles.css',
}

RUTUBE_VIDEOS = [
    {'title': 'Спокойная музыка и природа', 'embed': 'https://rutube.ru/play/embed/5f3b6fbe9b2b2ba44ca6203f7af579a3/'},
    {'title': 'Расслабляющее видео для отдыха', 'embed': 'https://rutube.ru/play/embed/6a4d1f7c01f43084f0ddf7d77be66ef4/'},
    {'title': 'Мотивационное видео для школьников', 'embed': 'https://rutube.ru/play/embed/8ad0f4e6df4e73f6efd6a838f438e2d5/'},
]

TOKEN = {'value': None, 'exp': 0}


def _json_bytes(data):
    return json.dumps(data, ensure_ascii=False).encode('utf-8')


def _contains_bad_words(text: str) -> bool:
    low = text.lower()
    return any(word in low for word in BAD_WORDS)


def _collect_files(kind: str):
    exts = MUSIC_EXTS if kind == 'music' else PHOTO_EXTS
    candidates = [ROOT, ROOT / kind, ROOT / 'media' / kind]
    found = {}
    for folder in candidates:
        if not folder.exists() or not folder.is_dir():
            continue
        for p in folder.iterdir():
            if p.is_file() and p.suffix.lower() in exts and p.name not in found:
                found[p.name] = p
    return found


def _fallback_reply(msg: str) -> str:
    t = msg.lower()
    if 'трев' in t or 'страш' in t:
        return 'Понимаю, что сейчас тревожно. Попробуй дыхание 4-4-4: вдох 4 сек, выдох 4 сек, 4 раза. Хочешь — разберём ситуацию по шагам.'
    if 'ссор' in t or 'конфликт' in t:
        return 'Конфликты тяжело переживаются. Попробуй спокойно описать чувство: «Мне неприятно, когда...». Могу помочь подобрать слова.'
    return 'Я рядом и готов поддержать. Расскажи, что случилось и что ты сейчас чувствуешь.'


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
            {'role': 'system', 'content': 'Ты доброжелательный школьный психолог. Отвечай по-русски кратко и поддерживающе.'},
            {'role': 'user', 'content': message},
        ],
    }
    req = request.Request(
        GIGACHAT_API_URL,
        data=_json_bytes(payload),
        method='POST',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        },
    )
    with request.urlopen(req, timeout=25) as resp:
        data = json.loads(resp.read().decode())
    return data.get('choices', [{}])[0].get('message', {}).get('content', 'Я рядом и готов помочь.')


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, code, data):
        body = _json_bytes(data)
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path, mime: str):
        data = path.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        path = parse.urlparse(self.path).path

        if path == '/api/videos':
            return self._send_json(200, {'items': RUTUBE_VIDEOS})

        m = re.fullmatch(r'/api/media/(music|photos)', path)
        if m:
            kind = m.group(1)
            files = _collect_files(kind)
            items = [{'name': name, 'url': f'/media/{parse.quote(name)}'} for name in sorted(files.keys())]
            return self._send_json(200, {'type': kind, 'items': items})

        if path.startswith('/media/'):
            name = parse.unquote(path.replace('/media/', '', 1))
            if '/' in name or '..' in name:
                return self._send_json(404, {'error': 'Not found'})
            files = _collect_files('music')
            files.update(_collect_files('photos'))
            target = files.get(name)
            if not target:
                return self._send_json(404, {'error': 'Not found'})
            ext = target.suffix.lower()
            mime = {
                '.mp3': 'audio/mpeg', '.wav': 'audio/wav', '.ogg': 'audio/ogg', '.m4a': 'audio/mp4',
                '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp', '.gif': 'image/gif',
            }.get(ext, 'application/octet-stream')
            return self._send_file(target, mime)

        if path in STATIC_FILES:
            p = ROOT / STATIC_FILES[path]
            if p.exists():
                mime = 'text/html; charset=utf-8' if p.suffix == '.html' else 'application/javascript; charset=utf-8' if p.suffix == '.js' else 'text/css; charset=utf-8'
                return self._send_file(p, mime)

        index = ROOT / 'index.html'
        if index.exists():
            return self._send_file(index, 'text/html; charset=utf-8')
        return self._send_json(404, {'error': 'Not found'})

    def do_POST(self):
        path = parse.urlparse(self.path).path
        if path != '/api/chat':
            return self._send_json(404, {'error': 'Not found'})

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
                reply = _ask_gigachat(message)
                return self._send_json(200, {'reply': reply, 'source': 'gigachat'})
            return self._send_json(200, {'reply': _fallback_reply(message), 'source': 'local-fallback'})
        except Exception as e:
            return self._send_json(200, {'reply': _fallback_reply(message), 'source': 'local-fallback', 'note': f'gigachat_error: {e}'})


if __name__ == '__main__':
    print(f'Островок уверенности: http://{HOST}:{PORT}')
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
