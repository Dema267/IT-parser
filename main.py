import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'jobs.db')
TABLE_NAME = "project_metrics"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            source TEXT NOT NULL,
            vacancies_count INTEGER NOT NULL,
            parsing_time REAL NOT NULL,
            salary_percent REAL NOT NULL,
            error_count INTEGER NOT NULL,
            ui_response_time REAL NOT NULL,
            comment TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Гарантированно создаем таблицу при импорте
init_db()