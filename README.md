# Multimedia Hub (Python + Tkinter)

Приложение с UI, которое умеет:

- воспроизводить музыку (из файлов проекта),
- открывать видео (из файлов проекта),
- просматривать картинки (из файлов проекта),
- решать 2 головоломки: **Пятнашки** и **Найди пару**,
- отправлять запросы в GigaChat с фильтрами,
- переключать тему интерфейса (светлая/тёмная).

## Важно про файлы

Музыка, видео и изображения берутся из **корня проекта** (папка, где лежит `app.py`) и вложенных директорий.
В интерфейсе есть кнопка **"Обновить файлы проекта"** — она пересканирует файлы.

## Установка

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Настройка GigaChat

Настройки убраны из UI и читаются из переменных окружения:

- `GIGACHAT_CLIENT_ID`
- `GIGACHAT_CLIENT_SECRET`

Пример (Linux/macOS):

```bash
export GIGACHAT_CLIENT_ID="..."
export GIGACHAT_CLIENT_SECRET="..."
```

Пример (Windows PowerShell):

```powershell
$env:GIGACHAT_CLIENT_ID="..."
$env:GIGACHAT_CLIENT_SECRET="..."
```

## Запуск

```bash
python app.py
```

> Примечание: в демонстрационном коде запросы к GigaChat идут с `verify=False`. Для production лучше настроить валидные сертификаты.
