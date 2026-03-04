# Интерактивный школьный сайт

Сайт включает:
- 5 головоломок;
- просмотр видео;
- просмотр изображений;
- прослушивание музыки;
- обращение к ИИ GigaChat через серверную часть;
- 5 переключаемых тем;
- плавные анимации интерфейса.

## Локальный запуск

```bash
npm install
npm start
```

Сайт будет доступен на `http://localhost:3000`.

## Переменные окружения

Создайте `.env` в корне:

```env
PORT=3000
GIGACHAT_AUTH_KEY=ВАШ_BASE64_CLIENTID_CLIENTSECRET
GIGACHAT_SCOPE=GIGACHAT_API_PERS
GIGACHAT_MODEL=GigaChat
# Необязательно:
# GIGACHAT_AUTH_URL=https://ngw.devices.sberbank.ru:9443/api/v2/oauth
# GIGACHAT_API_URL=https://gigachat.devices.sberbank.ru/api/v1/chat/completions
```

> Важно: ключи и токены хранятся только на сервере. Клиент отправляет запрос в `/api/gigachat`.

## Размещение на REG.RU (Node.js)

1. Создайте Node.js приложение на хостинге REG.RU.
2. Загрузите файлы проекта в директорию приложения.
3. Выполните `npm install`.
4. Добавьте переменные окружения (`GIGACHAT_AUTH_KEY` и др.) в панели REG.RU.
5. В качестве команды запуска установите: `npm start`.
6. Убедитесь, что порт берётся из `process.env.PORT` (уже реализовано в `server.js`).
