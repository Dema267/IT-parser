import sqlite3
from sqlite3 import Error
import os
from typing import Any, List, Optional, Dict
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='database.log'
)
logger = logging.getLogger(__name__)


def get_db_path() -> str:
    """Возвращает путь к файлу базы данных"""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'vacancies.db')


def create_connection():
    """Создает соединение с базой данных"""
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Ошибка при создании соединения с БД: {e}")
        raise


def migrate_add_original_url_column(conn):
    """Добавляет столбец original_url, если его нет."""
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(vacancies)")
        columns = [row[1] for row in cursor.fetchall()]
        if "original_url" not in columns:
            cursor.execute(
                "ALTER TABLE vacancies ADD COLUMN original_url TEXT NOT NULL DEFAULT ''"
            )
            conn.commit()
            print("Столбец original_url успешно добавлен.")
    except Error as e:
        print(f"Ошибка миграции original_url: {e}")


def initialize_database():
    """Инициализирует базу данных"""
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # Создаем таблицу вакансий
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vacancies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT NOT NULL,
                salary TEXT,
                description TEXT,
                published_at DATETIME NOT NULL,
                source TEXT NOT NULL,
                original_url TEXT NOT NULL,
                UNIQUE(title, company, published_at)
            )
        """)

        conn.commit()
        conn.close()
        logger.info("База данных успешно инициализирована")
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")
        raise


def create_table(conn) -> None:
    """Создает таблицу для хранения вакансий."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS vacancies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT NOT NULL,
                salary TEXT,
                description TEXT,
                published_at DATETIME NOT NULL,
                source TEXT NOT NULL,
                original_url TEXT NOT NULL,
                UNIQUE(title, company, published_at)
            )
            """
        )
        conn.commit()
    except Error as e:
        print(f"Error of creating table: {e}")


def insert_vacancy(vacancy: Dict[str, Any]) -> bool:
    """Добавляет вакансию в базу данных"""
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO vacancies (
                title, company, location, salary, 
                description, published_at, source, original_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            vacancy['title'],
            vacancy['company'],
            vacancy['location'],
            vacancy.get('salary'),
            vacancy.get('description', ''),
            vacancy['published_at'],
            vacancy['source'],
            vacancy['original_url']
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Ошибка при добавлении вакансии: {e}")
        return False


def get_all_vacancies() -> List[Dict[str, Any]]:
    """Получает все вакансии из базы данных"""
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vacancies ORDER BY published_at DESC")
        vacancies = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return vacancies
    except Exception as e:
        logger.error(f"Ошибка при получении всех вакансий: {e}")
        return []


def search_vacancies(query: str) -> List[Dict[str, Any]]:
    """Поиск вакансий по запросу"""
    try:
        conn = create_connection()
        cursor = conn.cursor()
        search_pattern = f"%{query}%"
        cursor.execute("""
            SELECT * FROM vacancies 
            WHERE title LIKE ? 
            OR company LIKE ? 
            OR description LIKE ?
            ORDER BY published_at DESC
        """, (search_pattern, search_pattern, search_pattern))
        vacancies = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return vacancies
    except Exception as e:
        logger.error(f"Ошибка при поиске вакансий: {e}")
        return []


def get_filtered_vacancies(
        query="",
        location="",
        company="",
        page=1,
        per_page=50,
        order_by="id",
        order_direction="DESC",
) -> list:
    """
    Получает отфильтрованные вакансии из базы данных с поддержкой пагинации.
    Фильтрация выполняется на уровне SQL запроса для повышения производительности.
    """
    conn = create_connection()
    vacancies = []
    try:
        cursor = conn.cursor()
        # Базовый SQL запрос
        sql = "SELECT id, title, company, location, salary, description, published_at, source, original_url FROM vacancies WHERE 1=1"
        params = []
        # Добавляем условия для фильтрации
        if query:
            sql += " AND (title LIKE ? OR company LIKE ? OR location LIKE ? OR description LIKE ?)"
            params.extend(["%" + query + "%"] * 4)
        if location:
            sql += " AND location LIKE ?"
            params.append("%" + location + "%")
        if company:
            sql += " AND company LIKE ?"
            params.append("%" + company + "%")
        # Добавляем сортировку и пагинацию
        sql += f" ORDER BY {order_by} {order_direction} LIMIT ? OFFSET ?"
        offset = (page - 1) * per_page
        params.extend([per_page, offset])
        # Выполняем запрос
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        # Преобразуем результаты в список словарей
        for row in rows:
            vacancy = {
                "id": row[0],
                "title": row[1],
                "company": row[2],
                "location": row[3],
                "salary": row[4],
                "description": row[5],
                "published_at": row[6],
                "source": row[7],
                "original_url": row[8],
            }
            vacancies.append(vacancy)
    except Error as e:
        print(f"Error getting filtered vacancies: {e}")
    finally:
        conn.close()
    return vacancies


def get_total_vacancies_count(query="", location="", company="") -> int:
    """Возвращает общее количество вакансий"""
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # Базовый SQL запрос
        sql = "SELECT COUNT(*) FROM vacancies WHERE 1=1"
        params = []

        # Добавляем условия фильтрации
        if query:
            sql += " AND (title LIKE ? OR company LIKE ? OR description LIKE ?)"
            search_pattern = f"%{query}%"
            params.extend([search_pattern] * 3)

        if location:
            sql += " AND location LIKE ?"
            params.append(f"%{location}%")

        if company:
            sql += " AND company LIKE ?"
            params.append(f"%{company}%")

        cursor.execute(sql, params)
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        logger.error(f"Ошибка при подсчете вакансий: {e}")
        return 0


def remove_duplicates() -> None:
    """Удаляет дубликаты вакансий из базы данных"""
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # Создаем временную таблицу с уникальными вакансиями
        cursor.execute("""
            CREATE TEMPORARY TABLE temp_vacancies AS
            SELECT MIN(id) as id
            FROM vacancies
            GROUP BY title, company, published_at
        """)

        # Удаляем все вакансии, кроме тех, что в временной таблице
        cursor.execute("""
            DELETE FROM vacancies
            WHERE id NOT IN (SELECT id FROM temp_vacancies)
        """)

        # Удаляем временную таблицу
        cursor.execute("DROP TABLE temp_vacancies")

        conn.commit()
        conn.close()
        logger.info("Дубликаты вакансий успешно удалены")
    except Exception as e:
        logger.error(f"Ошибка при удалении дубликатов: {e}")


def get_unique_sources() -> list:
    """Получает список уникальных источников вакансий"""
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT source FROM vacancies")
        sources = [row[0] for row in cursor.fetchall()]
        conn.close()
        return sources
    except Exception as e:
        logger.error(f"Ошибка при получении списка источников: {e}")
        return []


def get_unique_cities() -> list:
    """Получает список уникальных городов"""
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT location FROM vacancies")
        cities = [row[0] for row in cursor.fetchall()]
        conn.close()
        return cities
    except Exception as e:
        logger.error(f"Ошибка при получении списка городов: {e}")
        return []


def get_vacancies(limit: int = 50) -> List[Dict[str, Any]]:
    """Получает список вакансий с ограничением по количеству"""
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vacancies ORDER BY published_at DESC LIMIT ?", (limit,))
        vacancies = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return vacancies
    except Exception as e:
        logger.error(f"Ошибка при получении списка вакансий: {e}")
        return []


def get_vacancy_by_id(vacancy_id: int) -> Optional[Dict[str, Any]]:
    """Получает вакансию по ID"""
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vacancies WHERE id = ?", (vacancy_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"Ошибка при получении вакансии по ID {vacancy_id}: {e}")
        return None


def get_vacancies_by_source(source: str) -> List[Dict[str, Any]]:
    """Получает вакансии по источнику"""
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vacancies WHERE source = ? ORDER BY published_at DESC", (source,))
        vacancies = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return vacancies
    except Exception as e:
        logger.error(f"Ошибка при получении вакансий по источнику {source}: {e}")
        return []


if __name__ == "__main__":
    initialize_database()