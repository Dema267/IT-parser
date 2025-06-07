import sqlite3
from datetime import datetime

DB_NAME = 'metrics.db'
TABLE_NAME = 'project_metrics'

def init_db():
    """Создаёт таблицу метрик, если она не существует."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                source TEXT,
                vacancies_count INTEGER,
                parsing_time REAL,
                salary_percent TEXT,
                error_count INTEGER,
                ui_response_time INTEGER,
                comment TEXT
            )
        ''')
        conn.commit()
        print(f"[✓] Таблица '{TABLE_NAME}' инициализирована в '{DB_NAME}'.")

def log_metrics(data: dict):
    """Добавляет строку метрик в базу данных."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            INSERT INTO {TABLE_NAME} (
                date, source, vacancies_count, parsing_time, 
                salary_percent, error_count, ui_response_time, comment
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().strftime('%Y-%m-%d'),
            data.get('source'),
            data.get('vacancies_count'),
            data.get('parsing_time'),
            data.get('salary_percent'),
            data.get('error_count'),
            data.get('ui_response_time'),
            data.get('comment')
        ))
        conn.commit()
        print(f"[+] Метрики добавлены: {data}")

if __name__ == '__main__':
    init_db()

    # Пример использования
    example_data = {
        'source': 'HH',
        'vacancies_count': 1400,
        'parsing_time': 10.3,
        'salary_percent': '81%',
        'error_count': 2,
        'ui_response_time': 120,
        'comment': 'Запуск с оптимизацией пагинации'
    }

    log_metrics(example_data)
