# Multimedia Hub (Python + Tkinter)

Приложение с UI, которое умеет:

- воспроизводить музыку,
- выбирать видео и показывать информацию о выбранном файле,
- просматривать картинки,
- решать 2 головоломки на отдельных подстраницах: **Пазл с эмодзи** и **Найди пару**,
- отправлять запросы в GigaChat.

## Изменения

- Убраны любые упоминания внешнего плеера из вкладки видео.
- Убрана фильтрация сообщений для GigaChat.
- Интерфейс обновлён: более аккуратные отступы, стили кнопок, улучшены цвета светлой/тёмной темы.

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
