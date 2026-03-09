# Пакет для запуска на REG.RU

Эта папка содержит все файлы, необходимые для запуска сайта на хостинге/VPS REG.RU.

## Состав
- `server.js`
- `package.json`
- `Dockerfile`
- `.dockerignore`
- `.env.example`
- `index.html`
- `app.js`
- `styles.css`
- `music/`, `videos/`, `photos/` (медиа из корня)
- также поддерживаются `media/music`, `media/videos`, `media/photos`

## Быстрый запуск (Node.js)
1. Скопируйте папку `reg_ru_deploy` на сервер.
2. Перейдите в нее:
   ```bash
   cd reg_ru_deploy
   ```
3. Создайте `.env`:
   ```bash
   cp .env.example .env
   ```
4. Запустите:
   ```bash
   npm start
   ```

## Запуск через Docker
```bash
docker build -t ostrovok-uverennosti .
docker run -d --name ostrovok -p 3000:3000 --env-file .env ostrovok-uverennosti
```
