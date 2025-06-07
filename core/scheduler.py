import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from typing import List, Dict, Any
from core.database import insert_vacancy, remove_duplicates
from parsers.hh_parser import HHAPIParser
from parsers.sj_parser import SJAPIParser
from parsers.fl_parser import FLParser

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='scheduler.log'
)
logger = logging.getLogger(__name__)

# Создаем планировщик
scheduler = BackgroundScheduler()


def parse_jobs():
    """Парсинг вакансий со всех источников"""
    try:
        logger.info("Начало парсинга вакансий")

        # Инициализируем парсеры
        hh_parser = HHAPIParser()
        sj_parser = SJAPIParser()
        fl_parser = FLParser()

        # Парсим вакансии с каждого источника
        hh_vacancies = hh_parser.parse_vacancies()
        sj_vacancies = sj_parser.parse_vacancies()
        fl_vacancies = fl_parser.parse_vacancies()

        # Сохраняем вакансии в базу данных
        total_saved = 0
        for vacancy in hh_vacancies + sj_vacancies + fl_vacancies:
            vacancy_dict = {
                'title': vacancy.title,
                'company': vacancy.company,
                'location': vacancy.location,
                'salary': vacancy.salary,
                'description': vacancy.description,
                'published_at': vacancy.published_at,
                'source': vacancy.source,
                'original_url': vacancy.original_url
            }
            if insert_vacancy(vacancy_dict):
                total_saved += 1

        # Удаляем дубликаты
        remove_duplicates()

        logger.info(f"Парсинг завершен. Сохранено {total_saved} вакансий")

    except Exception as e:
        logger.error(f"Ошибка при парсинге вакансий: {e}")


def start_scheduler():
    """Запускает планировщик задач"""
    try:
        # Добавляем задачу парсинга каждый час
        scheduler.add_job(
            parse_jobs,
            trigger=IntervalTrigger(hours=1),
            id='parse_jobs',
            name='Parse job vacancies',
            replace_existing=True
        )

        # Запускаем планировщик
        scheduler.start()

        # Запускаем парсинг сразу при старте
        parse_jobs()

        logger.info("Планировщик успешно запущен")
    except Exception as e:
        logger.error(f"Ошибка при запуске планировщика: {e}")


def stop_scheduler():
    """Останавливает планировщик задач"""
    try:
        scheduler.shutdown()
        logger.info("Планировщик успешно остановлен")
    except Exception as e:
        logger.error(f"Ошибка при остановке планировщика: {e}")


# Экспортируем функции
__all__ = ['start_scheduler', 'stop_scheduler', 'parse_jobs']