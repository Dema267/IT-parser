from flask import Flask, render_template
import sqlite3
import os

app = Flask(__name__)

DB_NAME = 'metrics.db'
TABLE_NAME = 'project_metrics'

# --- Создание таблицы, если не существует ---
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                source TEXT,
                vacancies_count INTEGER,
                parsing_time REAL,
                salary_percent REAL,
                error_count INTEGER,
                ui_response_time REAL,
                comment TEXT
            )
        ''')
        conn.commit()

# --- Вставка одной тестовой записи, если таблица пуста ---
def insert_dummy_metrics():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute(f'''
                INSERT INTO {TABLE_NAME} (
                    date, source, vacancies_count, parsing_time,
                    salary_percent, error_count, ui_response_time, comment
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                '2025-05-03', 'hh.ru', 120, 3.5, 78.3, 2, 0.45, 'Тестовая запись'
            ))
            conn.commit()

# --- Получение всех метрик ---
def get_metrics():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT date, source, vacancies_count, parsing_time,
                   salary_percent, error_count, ui_response_time, comment
            FROM {TABLE_NAME}
            ORDER BY id DESC
        ''')
        rows = cursor.fetchall()
    return rows

# --- Роут отображения ---
@app.route('/')
def index():
    metrics = get_metrics()
    return render_template('metrics.html', metrics=metrics)

# --- Точка входа ---
if __name__ == '__main__':
    init_db()
    insert_dummy_metrics()
    app.run(debug=True)
