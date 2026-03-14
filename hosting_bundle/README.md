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
Плеер в интерфейсе запускается по кнопке трека и показывает «Сейчас играет», без отдельной чёрной панели контролов.

## 3) ИИ на Python (только API чата)
```bash
cp .env.example .env
python3 server.py
```
По умолчанию: `http://localhost:8001/api/chat`

### Authorization Key для ИИ
- В `.env` задайте:
```bash
AUTHORIZATION_KEY=your_secret_key
```
- На фронтенде перед `app.js` передайте ключ:
```html
<script>
  window.AI_BACKEND_URL = "https://your-ai-host.example";
  window.AUTHORIZATION_KEY = "your_secret_key";
</script>
```
- Тогда запросы к `/api/chat` будут идти с заголовком:
`Authorization: Bearer <ключ>`.

При необходимости на странице можно переопределить адрес ИИ:
```html
<script>window.AI_BACKEND_URL = "https://your-ai-host.example";</script>
```

## 4) Видео
Видео встроены с Rutube (iframe), локальные видеофайлы не нужны.

### Как добавить новые видео с Rutube
1. Откройте нужное видео на Rutube.
2. Нажмите «Поделиться» → «Код для вставки».
3. Возьмите URL вида `https://rutube.ru/play/embed/<ID>/`.
4. Добавьте его в массив `RUTUBE_VIDEOS` в `app.js` в формате:
```js
{ title: 'Название видео', embed: 'https://rutube.ru/play/embed/<ID>/' }
```
5. Сохраните `app.js` и обновите страницу — новая кнопка появится в блоке «🎬 Видео».
