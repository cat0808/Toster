# Multimedia Hub (Python + Tkinter)

Приложение с UI, которое умеет:

- воспроизводить музыку,
- выбирать видео и показывать информацию о выбранном файле,
- просматривать картинки,
- решать 2 головоломки на отдельных подстраницах: **Пазл с эмодзи** и **Найди пару**,
- отправлять запросы в GigaChat.

## Что изменено в логике

- Фильтры GigaChat убраны из UI и применяются автоматически к сообщениям.
- Поле ответа GigaChat только для чтения (редактирование отключено).
- Для музыки/видео/картинок можно выбирать файлы, найденные в папке проекта и вложенных директориях.
- Вкладка видео больше не открывает внешний плеер.

## Установка

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Настройка GigaChat

Настройки читаются из переменных окружения:

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
