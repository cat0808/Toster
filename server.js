const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const PORT = Number(process.env.PORT) || 3000;
const root = __dirname;

const GIGACHAT_AUTH_URL = process.env.GIGACHAT_AUTH_URL || 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth';
const GIGACHAT_API_URL = process.env.GIGACHAT_API_URL || 'https://gigachat.devices.sberbank.ru/api/v1/chat/completions';
const GIGACHAT_SCOPE = process.env.GIGACHAT_SCOPE || 'GIGACHAT_API_PERS';
const GIGACHAT_MODEL = process.env.GIGACHAT_MODEL || 'GigaChat';

let cachedToken = null;
let tokenExpiresAt = 0;

const contentTypes = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp'
};

async function getGigaChatToken() {
  const now = Date.now();
  if (cachedToken && now < tokenExpiresAt - 20_000) return cachedToken;

  const authKey = process.env.GIGACHAT_AUTH_KEY;
  if (!authKey) throw new Error('GIGACHAT_AUTH_KEY is not configured on server');

  const response = await fetch(GIGACHAT_AUTH_URL, {
    method: 'POST',
    headers: {
      Authorization: `Basic ${authKey}`,
      RqUID: crypto.randomUUID(),
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({ scope: GIGACHAT_SCOPE })
  });

  if (!response.ok) {
    throw new Error(`GigaChat auth failed: ${response.status} ${await response.text()}`);
  }

  const data = await response.json();
  cachedToken = data.access_token;
  tokenExpiresAt = typeof data.expires_at === 'number' ? data.expires_at : Date.now() + 25 * 60 * 1000;
  return cachedToken;
}

function sendJson(res, statusCode, payload) {
  res.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=utf-8',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
  });
  res.end(JSON.stringify(payload));
}

async function handleApi(req, res) {
  if (req.method === 'OPTIONS') return sendJson(res, 200, { ok: true });

  if (req.method !== 'POST') return sendJson(res, 405, { error: 'Method not allowed' });

  let body = '';
  req.on('data', (chunk) => {
    body += chunk;
  });

  req.on('end', async () => {
    try {
      const parsed = JSON.parse(body || '{}');
      const prompt = parsed.prompt;

      if (!prompt || typeof prompt !== 'string') {
        return sendJson(res, 400, { error: 'Введите текст запроса.' });
      }

      const token = await getGigaChatToken();
      const response = await fetch(GIGACHAT_API_URL, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: GIGACHAT_MODEL,
          messages: [
            { role: 'system', content: 'Ты полезный и дружелюбный ассистент для школьного сайта.' },
            { role: 'user', content: prompt }
          ],
          temperature: 0.7,
          max_tokens: 512
        })
      });

      if (!response.ok) {
        return sendJson(res, response.status, { error: `Ошибка GigaChat: ${await response.text()}` });
      }

      const data = await response.json();
      const answer = data?.choices?.[0]?.message?.content || 'Нет ответа от модели.';
      return sendJson(res, 200, { answer });
    } catch (error) {
      return sendJson(res, 500, { error: error.message || 'Внутренняя ошибка сервера' });
    }
  });
}

function serveFile(reqPath, res) {
  const safePath = path.normalize(reqPath).replace(/^\.\.?(\/|\\|$)/, '');
  const filePath = path.join(root, 'public', safePath === '/' ? 'index.html' : safePath);

  fs.readFile(filePath, (err, data) => {
    if (err) {
      fs.readFile(path.join(root, 'public', 'index.html'), (indexErr, indexData) => {
        if (indexErr) {
          res.writeHead(500, { 'Content-Type': 'text/plain; charset=utf-8' });
          return res.end('Server error');
        }
        res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
        return res.end(indexData);
      });
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    res.writeHead(200, { 'Content-Type': contentTypes[ext] || 'application/octet-stream' });
    res.end(data);
  });
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);

  if (url.pathname === '/api/gigachat') {
    handleApi(req, res);
    return;
  }

  serveFile(url.pathname, res);
});

server.listen(PORT, () => {
  console.log(`Server started at http://localhost:${PORT}`);
});
