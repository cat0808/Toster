# Multimedia Hub (Python + Tkinter)

Приложение с UI-интерфейсом, которое умеет:

- включать музыку и менять её параметры (громкость, скорость, EQ-пресеты),
- выбирать и открывать видео,
- запускать головоломку 15-puzzle,
- просматривать картинки,
- отправлять запросы в GigaChat с включаемыми фильтрами.

## Установка

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Запуск

```bash
python app.py
```

## GigaChat

Во вкладке **ИИ / GigaChat** введите:

- `Client ID`
- `Client Secret`

> Примечание: для демонстрации запросов в коде отключена SSL-проверка (`verify=False`) из-за частых проблем с локальными сертификатами. Для продакшена лучше настроить валидный CA bundle.
