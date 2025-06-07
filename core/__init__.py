# core/__init__.py

# Этот файл может быть пустым или содержать инициализацию пакета.
# Например, можно импортировать здесь основные модули, чтобы они были доступны при импорте пакета.

from .config import Config
from .database import (
    initialize_database,
    get_all_vacancies,
    insert_vacancy,
    search_vacancies,
    get_vacancies,
    get_vacancy_by_id,
    get_vacancies_by_source,
    remove_duplicates
)
from .scheduler import start_scheduler

__all__ = [
    'initialize_database',
    'get_all_vacancies',
    'insert_vacancy',
    'search_vacancies',
    'get_vacancies',
    'get_vacancy_by_id',
    'get_vacancies_by_source',
    'start_scheduler',
    'remove_duplicates'
]

def create_db():
    # Инициализация базы данных
    initialize_database()