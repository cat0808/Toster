# Островок уверенности — пакет для хостинга (одна папка)

В этой папке лежат **все файлы сайта** для хостинга:
- `index.html`
- `app.js`
- `styles.css`
- `media-manifest.json`
- `.env.example`
- `server.py` (ТОЛЬКО ИИ backend `/api/chat`)

## 1) Хостинг сайта
Разместите `index.html`, `app.js`, `styles.css`, `media-manifest.json` на статическом хостинге.

## 2) Музыка и фото
Укажите файлы в `media-manifest.json`, например:
```json
{
  "music": ["song1.mp3", "song2.mp3"],
  "photos": ["photo1.jpg", "photo2.png"]
}
```
Файлы должны лежать рядом с сайтом (в той же корневой директории хостинга или по указанным URL).

## 3) ИИ на Python (только API чата)
```bash
cp .env.example .env
python3 server.py
```
По умолчанию: `http://localhost:8001/api/chat`

При необходимости на странице можно переопределить адрес:
```html
<script>window.AI_BACKEND_URL = "https://your-ai-host.example";</script>
```

## 4) Видео
Видео встроены с Rutube (iframe), локальные видеофайлы не нужны.
