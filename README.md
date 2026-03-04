# Мультимедиа сайт (Flask)

Проект запускается как сайт и может быть собран в **одну чистую папку** без `.git` и лишнего.

## Быстрый запуск (в 1 клик)

В корне проекта есть запускаторы:

- `run_site.bat` — Windows
- `run_site.sh` — Linux/macOS

Они запускают `start_site.py`, который:
1. Проверяет зависимости,
2. При необходимости ставит их из `requirements.txt`,
3. Поднимает сайт на `http://127.0.0.1:5000`,
4. Пытается автоматически открыть браузер.

## Как собрать «чистую» папку без Git

Запустите:

```bash
python make_portable_bundle.py
```

Появится папка `PortableSite/` — в ней только нужное для запуска сайта:

- `webapp.py`
- `start_site.py`
- `run_site.bat` / `run_site.sh`
- `requirements.txt`
- `static/`, `templates/`, `media/`
- `wsgi.py`, `passenger_wsgi.py`
- `README.md`

Эту папку можно просто перенести/заархивировать и запускать отдельно от репозитория.

## Куда класть медиафайлы

Складывайте музыку, видео и изображения в `media/` (подпапки поддерживаются).

Пример:

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

## Деплой на REG.RU

- Shared hosting (Passenger): используйте `passenger_wsgi.py`.
- VPS: используйте Gunicorn:

```bash
gunicorn -w 2 -b 0.0.0.0:8000 wsgi:application
```

## Важно

В демо-коде запросы к GigaChat идут с `verify=False`. Для production рекомендуется включить проверку TLS-сертификатов.
