# Job Parser

Парсер вакансий с различных платформ (HH.ru, SuperJob.ru, FL.ru) для упрощения поиска работы.

## Возможности

- Парсинг вакансий с HH.ru через официальное API
- Парсинг вакансий с SuperJob.ru через официальное API
- Парсинг вакансий с FL.ru
- Сохранение вакансий в SQLite базу данных
- Веб-интерфейс для просмотра вакансий
- Возможность фильтрации и поиска по сохраненным вакансиям

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/job_parser.git
cd job_parser
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv .venv
source .venv/bin/activate  # для Linux/Mac
.venv\Scripts\activate     # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл .env в корневой директории проекта и добавьте необходимые API ключи:
```
SJ_API_KEY=your_superjob_api_key
```

## Использование

1. Запуск парсера:
```bash
python run.py
```

2. Запуск веб-интерфейса:
```bash
python parsers/app.py
```

3. Просмотр сохраненных вакансий через консоль:
```bash
python parsers/view_vakancies.py
```

## Структура проекта

- `parsers/` - модули парсеров для разных платформ
- `app/` - веб-приложение
- `services/` - вспомогательные сервисы
- `metrics/` - модули для сбора метрик
- `tests/` - тесты
- `migrations/` - миграции базы данных

## Требования

- Python 3.8+
- SQLite3
- Зависимости из requirements.txt

## Лицензия

MIT
