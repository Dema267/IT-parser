from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from typing import List
import logging
from job_parser.parsers.hh_parser import HHAPIParser, Vacancy
from job_parser.parsers.sj_parser import SJAPIParser
from job_parser.parsers.fl_parser import FLParser
from job_parser.core.config import config
from job_parser.core.database import insert_vacancy, remove_duplicates

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_vacancies(search_query: str = "Python") -> List[Vacancy]:
    """Обновляет вакансии в базе данных из всех источников."""
    logger.info(f"Запуск обновления вакансий для запроса: '{search_query}'")

    all_vacancies = []

    try:
        # Парсинг HeadHunter
        logger.info("Парсинг HeadHunter...")
        hh_parser = HHAPIParser()
        hh_vacancies = hh_parser.parse_vacancies(search_query)
        all_vacancies.extend(hh_vacancies)
        logger.info(f"Найдено {len(hh_vacancies)} вакансий на HH")

        # Парсинг SuperJob
        if config.SJ_API_KEY:
            logger.info("Парсинг SuperJob...")
            sj_parser = SJAPIParser(config.SJ_API_KEY)
            sj_vacancies = sj_parser.parse_vacancies(search_query)
            all_vacancies.extend(sj_vacancies)
            logger.info(f"Найдено {len(sj_vacancies)} вакансий на SJ")
        else:
            logger.warning("API ключ для SuperJob не указан, пропускаем")

        # Парсинг FL.ru
        logger.info("Парсинг FL.ru...")
        fl_parser = FLParser()
        fl_vacancies = fl_parser.parse_vacancies(search_query)
        all_vacancies.extend(fl_vacancies)
        logger.info(f"Найдено {len(fl_vacancies)} вакансий на FL.ru")

        # Сохранение в БД
        logger.info("Сохранение в базу данных...")
        for vacancy in all_vacancies:
            insert_vacancy(vacancy)
        remove_duplicates()

        logger.info(f"Всего сохранено {len(all_vacancies)} вакансий")
        return all_vacancies

    except Exception as e:
        logger.error(f"Ошибка при обновлении вакансий: {str(e)}", exc_info=True)
        return []

def start_scheduler():
    """Запускает планировщик задач."""
    try:
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            update_vacancies,
            'interval',
            seconds=config.SCHEDULER_INTERVAL,
            kwargs={'search_query': config.SEARCH_QUERY}
        )
        scheduler.start()
        logger.info(f"Планировщик запущен с интервалом {config.SCHEDULER_INTERVAL} сек")
    except Exception as e:
        logger.error(f"Ошибка запуска планировщика: {str(e)}", exc_info=True)

if __name__ == "__main__":
    update_vacancies()
