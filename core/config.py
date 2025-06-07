# core/config.py

import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

class Config:
    # Пример конфигурации
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'parsers/vacancies.db')
    SJ_API_KEY = os.getenv("SJ_API_KEY", "v3.r.139040003.a8a7c7612fa80498a334a3f6d07ee655d3629be1.50b7a63c5ab8c028784ec64ca96d91c82673fa2d")
    SCHEDULER_INTERVAL = int(os.getenv('SCHEDULER_INTERVAL', 3600))  # Интервал в секундах
    SEARCH_QUERY = "Python"

config = Config()


