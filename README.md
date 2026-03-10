# Островок уверенности (минимальный запуск)

Минимальная версия для запуска сервера:
- `server.py` (Python backend + ИИ логика)
- `index.html`, `app.js`, `styles.css` (frontend)
- `.env.example`

## Запуск
```bash
cp .env.example .env
python3 server.py
```

Открыть: `http://localhost:3000`

## Медиа
Чтобы музыка и фото точно отображались, можно класть файлы **прямо в корень проекта**:
- музыка: `*.mp3`, `*.wav`, `*.ogg`, `*.m4a`
- фото: `*.jpg`, `*.jpeg`, `*.png`, `*.webp`, `*.gif`

Видео берутся с Rutube (через iframe), локальные видеофайлы не нужны.
