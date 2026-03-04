# Мультимедиа сайт (Flask)

Проект работает как веб-сайт на Flask и может быть развёрнут локально или на хостинге REG.RU.

## Возможности

- музыка, видео и картинки из папки `media/`;
- головоломки в браузере;
- ИИ-запросы через GigaChat;
- переключение цветных тем интерфейса.

## Установка

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Куда класть медиафайлы

Складывайте музыку, видео и изображения в папку `media/` в корне проекта. Подпапки поддерживаются.

Пример структуры:

```text
media/
  music/
    song.mp3
  video/
    clip.mp4
  images/
    photo.jpg
```

Поддерживаемые расширения:
- аудио: `.mp3`, `.wav`, `.flac`, `.ogg`, `.m4a`
- видео: `.mp4`, `.avi`, `.mkv`, `.mov`, `.webm`
- изображения: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.webp`

## Переменные окружения для ИИ

- `GIGACHAT_CLIENT_ID`
- `GIGACHAT_CLIENT_SECRET`

## Локальный запуск

```bash
python webapp.py
```

Откройте: `http://127.0.0.1:5000`

---

## Деплой на REG.RU

В проект добавлены WSGI entrypoints для хостинга:

- `passenger_wsgi.py` — для REG.RU shared hosting (Passenger);
- `wsgi.py` — универсальный WSGI entrypoint (например, для Gunicorn).

### Вариант 1: REG.RU shared hosting (Passenger)

1. Загрузите проект на хостинг (в папку сайта).
2. Установите зависимости в окружение хостинга:
   ```bash
   pip install -r requirements.txt
   ```
3. В панели REG.RU выберите Python-сайт/приложение и укажите файл запуска: `passenger_wsgi.py`.
4. Добавьте переменные окружения `GIGACHAT_CLIENT_ID` и `GIGACHAT_CLIENT_SECRET` в настройках хостинга (если используете ИИ).
5. Перезапустите приложение из панели.

### Вариант 2: VPS на REG.RU (Gunicorn + reverse proxy)

Запуск Gunicorn:

```bash
gunicorn -w 2 -b 0.0.0.0:8000 wsgi:application
```

Далее проксируйте через Nginx/Apache на ваш домен.

## Важно

В демонстрационном коде запросы к GigaChat выполняются с `verify=False`. Для production рекомендуется включить проверку TLS-сертификатов.
