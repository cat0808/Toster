# Островок уверенности — пакет для хостинга (одна папка)

В этой папке лежат **все файлы сайта** для хостинга:
- `index.html`
- `app.js`
- `styles.css`
- `media-manifest.json`
- `.env.example`
- `server.py` (ТОЛЬКО ИИ backend `/api/chat`, вход по Authorization Key)

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

## 3) ИИ на Python (только API чата, без GigaChat)
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
- На сайте в разделе чата введите этот ключ в поле **Authorization Key** и нажмите «Сохранить ключ».
- После этого сообщения в чат идут с заголовком:
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
3. Возьмите ссылку на видео вида `https://rutube.ru/video/<ID>/` или embed-ссылку `https://rutube.ru/play/embed/<ID>/`.
4. Добавьте его в массив `RUTUBE_VIDEOS` в `app.js` в формате:
```js
{ title: 'Название видео', url: 'https://rutube.ru/video/<ID>/' }
// или
{ title: 'Название видео', embed: 'https://rutube.ru/play/embed/<ID>/' }
```
5. Сохраните `app.js` и обновите страницу — новая кнопка появится в блоке «🎬 Видео».


## 5) Деплой на REG.RU

Ниже два рабочих сценария.

### Вариант A: только статический сайт (без ИИ)
1. В панели REG.RU откройте файловый менеджер сайта (обычно папка `public_html`).
2. Загрузите туда содержимое `hosting_bundle/`: `index.html`, `app.js`, `styles.css`, `media-manifest.json` и ваши медиа-файлы.
3. В `media-manifest.json` укажите реальные пути к музыке и картинкам.
4. Откройте домен и проверьте разделы «Музыка», «Картинки», «Видео», «Головоломки».

### Вариант B: сайт + Python ИИ backend
Рекомендуется VPS на REG.RU (Ubuntu 22.04+).

1. Скопируйте папку `hosting_bundle/` на сервер, например в `/opt/ostrovok`.
2. Создайте `.env` из примера и заполните ключи:
```bash
cd /opt/ostrovok
cp .env.example .env
```
3. Запустите backend:
```bash
python3 server.py
```
По умолчанию backend будет на `http://127.0.0.1:8001`.

4. Прокиньте backend через Nginx на HTTPS-домен, например `https://ai.your-domain.ru`.
Пример location:
```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8001/api/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

5. На фронте пропишите адрес backend:
```html
<script>
  window.AI_BACKEND_URL = "https://ai.your-domain.ru";
  window.AUTHORIZATION_KEY = "your_secret_key";
</script>
```

6. Проверьте запрос к ИИ на сервере:
```bash
curl -X POST https://ai.your-domain.ru/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_secret_key" \
  -d '{"message":"привет"}'
```

> Для production на REG.RU используйте HTTPS (Let's Encrypt) и не храните секретные ключи в публичном репозитории.


> Важно: для iframe используйте только `.../play/embed/...` (или обычный `.../video/...`, который автоматически конвертируется).
> Ссылки на главную/канал Rutube часто блокируются заголовком X-Frame-Options и не откроются во фрейме.
