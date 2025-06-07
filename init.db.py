import sqlite3

def create_metrics_table():
    conn = sqlite3.connect('jobs.db')  # путь к твоей БД
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            value REAL NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

create_metrics_table()
