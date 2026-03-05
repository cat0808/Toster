import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import crypto from 'node:crypto';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const argv = process.argv.slice(2);
const argMap = new Map();
for (let i = 0; i < argv.length; i += 1) {
  const token = argv[i];
  if (token.startsWith('--')) {
    const key = token.slice(2);
    const value = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[i + 1] : 'true';
    argMap.set(key, value);
  }
}

const HOST = argMap.get('host') || process.env.HOST || '127.0.0.1';
const PORT = Number(argMap.get('port') || process.env.PORT || 3000);
const GIGACHAT_CLIENT_ID = process.env.GIGACHAT_CLIENT_ID || '';
const GIGACHAT_CLIENT_SECRET = process.env.GIGACHAT_CLIENT_SECRET || '';
const GIGACHAT_AUTH_URL = process.env.GIGACHAT_AUTH_URL || 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth';
const GIGACHAT_API_URL = process.env.GIGACHAT_API_URL || 'https://gigachat.devices.sberbank.ru/api/v1/chat/completions';
const GIGACHAT_SCOPE = process.env.GIGACHAT_SCOPE || 'GIGACHAT_API_PERS';
const INAPPROPRIATE_WORDS = ['бляд', 'сука', 'хер', 'пизд', 'еб', 'нах', 'мраз', 'долбо', 'fuck', 'shit'];
let gigachatToken = null;
let tokenExpiresAt = 0;

const mediaConfig = {
  music: { dir: path.join(__dirname, 'media/music'), exts: ['.mp3', '.wav', '.ogg', '.m4a'] },
  videos: { dir: path.join(__dirname, 'media/videos'), exts: ['.mp4', '.webm', '.mov', '.m4v'] },
  photos: { dir: path.join(__dirname, 'media/photos'), exts: ['.jpg', '.jpeg', '.png', '.webp', '.gif'] }
};

const botSystemPrompt = `Ты — доброжелательный и эмпатичный школьный психолог по имени "Островок".
Давай короткие и практичные советы, учитывай возраст 10-17 лет.
Не диагностируй болезни и не назначай лечение.
Если запрос опасный или про причинение вреда — мягко предложи обратиться к взрослому/школьному психологу/службе помощи.
Отвечай по-русски.`;

function sendJson(res, code, data) {
  res.writeHead(code, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(data));
}

function sanitizePath(urlPath) {
  const normalized = path.normalize(urlPath).replace(/^([.][.][/\\])+/, '');
  return normalized === '/' ? '/index.html' : normalized;
}

async function listMedia(type) {
  const config = mediaConfig[type];
  if (!config) return [];
  try {
    const files = await fs.readdir(config.dir);
    return files
      .filter((file) => config.exts.includes(path.extname(file).toLowerCase()))
      .sort((a, b) => a.localeCompare(b, 'ru'))
      .map((file) => ({ name: file, url: `/media/${type}/${encodeURIComponent(file)}` }));
  } catch {
    return [];
  }
}

async function serveStatic(req, res) {
  const url = new URL(req.url || '/', `http://${req.headers.host}`);
  if (url.pathname.startsWith('/media/')) {
    const filePath = path.join(__dirname, decodeURIComponent(url.pathname));
    if (!filePath.startsWith(path.join(__dirname, 'media'))) return sendJson(res, 403, { error: 'Forbidden' });
    try {
      const stat = await fs.stat(filePath);
      if (!stat.isFile()) return sendJson(res, 404, { error: 'Not found' });
      const ext = path.extname(filePath).toLowerCase();
      const mime = {
        '.mp3': 'audio/mpeg', '.wav': 'audio/wav', '.ogg': 'audio/ogg', '.m4a': 'audio/mp4',
        '.mp4': 'video/mp4', '.webm': 'video/webm', '.mov': 'video/quicktime', '.m4v': 'video/x-m4v',
        '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp', '.gif': 'image/gif'
      }[ext] || 'application/octet-stream';
      res.writeHead(200, { 'Content-Type': mime });
      const buffer = await fs.readFile(filePath);
      return res.end(buffer);
    } catch {
      return sendJson(res, 404, { error: 'Not found' });
    }
  }

  const safePath = sanitizePath(url.pathname);
  const localPath = path.join(__dirname, 'public', safePath);
  if (!localPath.startsWith(path.join(__dirname, 'public'))) return sendJson(res, 403, { error: 'Forbidden' });
  try {
    const data = await fs.readFile(localPath);
    const ext = path.extname(localPath).toLowerCase();
    const mime = {
      '.html': 'text/html; charset=utf-8',
      '.css': 'text/css; charset=utf-8',
      '.js': 'application/javascript; charset=utf-8',
      '.json': 'application/json; charset=utf-8'
    }[ext] || 'application/octet-stream';
    res.writeHead(200, { 'Content-Type': mime });
    res.end(data);
  } catch {
    try {
      const html = await fs.readFile(path.join(__dirname, 'public/index.html'));
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      res.end(html);
    } catch {
      sendJson(res, 404, { error: 'Not found' });
    }
  }
}

function hasBadWords(text) {
  const lower = text.toLowerCase();
  return INAPPROPRIATE_WORDS.some((w) => lower.includes(w));
}


function buildLocalPsychologistReply(userMessage) {
  const text = userMessage.toLowerCase();
  if (text.includes('трев') || text.includes('страш')) {
    return 'Понимаю, что сейчас тревожно. Попробуй технику «4-4-4»: 4 секунды вдох, 4 секунды выдох, повтори 4 раза. Если хочешь, разберём твою ситуацию по шагам.';
  }
  if (text.includes('ссор') || text.includes('конфликт')) {
    return 'Ссоры очень выматывают. Попробуй сказать о своих чувствах через фразу «Мне неприятно, когда...», без обвинений. Могу помочь сформулировать спокойно.';
  }
  return 'Я рядом и готов поддержать. Расскажи, что произошло, что ты сейчас чувствуешь и чего больше всего хочешь от этой ситуации — разберём вместе.';
}

async function fetchGigachatToken() {
  if (!GIGACHAT_CLIENT_ID || !GIGACHAT_CLIENT_SECRET) {
    throw new Error('GIGACHAT credentials are not configured');
  }
  if (gigachatToken && Date.now() < tokenExpiresAt - 30_000) return gigachatToken;
  const auth = Buffer.from(`${GIGACHAT_CLIENT_ID}:${GIGACHAT_CLIENT_SECRET}`).toString('base64');
  const response = await fetch(GIGACHAT_AUTH_URL, {
    method: 'POST',
    headers: {
      Authorization: `Basic ${auth}`,
      'RqUID': crypto.randomUUID(),
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({ scope: GIGACHAT_SCOPE })
  });
  if (!response.ok) throw new Error(`Token request failed: ${response.status}`);
  const data = await response.json();
  gigachatToken = data.access_token;
  tokenExpiresAt = Date.now() + (data.expires_in || 1800) * 1000;
  return gigachatToken;
}

async function askGigachat(userMessage) {
  const token = await fetchGigachatToken();
  const response = await fetch(GIGACHAT_API_URL, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: process.env.GIGACHAT_MODEL || 'GigaChat',
      temperature: 0.7,
      messages: [
        { role: 'system', content: botSystemPrompt },
        { role: 'user', content: userMessage }
      ]
    })
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Gigachat failed ${response.status}: ${text.slice(0, 300)}`);
  }
  const data = await response.json();
  return data?.choices?.[0]?.message?.content || 'Мне нужно чуть больше информации, чтобы помочь.';
}

const server = http.createServer(async (req, res) => {
  if (!req.url) return sendJson(res, 400, { error: 'No URL' });

  if (req.method === 'GET' && req.url.startsWith('/api/media/')) {
    const type = req.url.split('/').pop();
    const items = await listMedia(type);
    return sendJson(res, 200, { type, items });
  }

  if (req.method === 'POST' && req.url === '/api/chat') {
    try {
      let raw = '';
      for await (const chunk of req) raw += chunk;
      const body = JSON.parse(raw || '{}');
      const message = String(body.message || '').trim();
      if (!message) return sendJson(res, 400, { error: 'Введите сообщение.' });

      if (hasBadWords(message)) {
        return sendJson(res, 200, {
          reply: 'Я хочу поддержать тебя, но не могу отвечать на сообщения с грубыми словами. Пожалуйста, переформулируй вопрос спокойнее 💙'
        });
      }

      if (!GIGACHAT_CLIENT_ID || !GIGACHAT_CLIENT_SECRET) {
        const reply = buildLocalPsychologistReply(message);
        return sendJson(res, 200, { reply, source: 'local-fallback' });
      }

      const reply = await askGigachat(message);
      return sendJson(res, 200, { reply, source: 'gigachat' });
    } catch (error) {
      return sendJson(res, 500, { error: `Ошибка чата: ${error.message}` });
    }
  }

  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    });
    return res.end();
  }

  return serveStatic(req, res);
});

server.listen(PORT, HOST, () => {
  console.log(`Островок уверенности запущен на http://${HOST}:${PORT}`);
  if (HOST === '127.0.0.1') {
    console.log(`Локальный адрес: http://localhost:${PORT}`);
  }
});
