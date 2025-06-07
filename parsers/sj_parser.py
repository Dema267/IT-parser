import requests
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging
from time import sleep

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='sj_parser.log'
)
logger = logging.getLogger(__name__)

SJ_API_URL = "https://api.superjob.ru/2.0/vacancies/"
REQUEST_DELAY = 0.5
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"


@dataclass
class Vacancy:
    title: str
    company: str
    location: str
    salary: Optional[str]
    description: str
    published_at: datetime
    source: str = "superjob.ru"
    original_url: str = ""


class SJAPIParser:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self._init_session()

    def _init_session(self):
        self.session = requests.Session()
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json"
        }
        if self.api_key:
            headers["X-Api-App-Id"] = self.api_key
        self.session.headers.update(headers)

    def _parse_salary(self, salary_data: Dict) -> Optional[str]:
        if not salary_data or salary_data.get("payment_from") == 0 and salary_data.get("payment_to") == 0:
            return None

        payment_from = salary_data.get("payment_from")
        payment_to = salary_data.get("payment_to")
        currency = salary_data.get("currency", "rub")

        parts = []
        if payment_from:
            parts.append(f"от {payment_from}")
        if payment_to:
            parts.append(f"до {payment_to}")

        return " ".join(parts) + f" {currency}" if parts else None

    def parse_vacancies(self, search_query: str = "Python", town: int = 4) -> List[Vacancy]:
        """Основной метод парсинга вакансий (town=4 - Москва)"""
        vacancies = []
        params = {
            "keyword": search_query,
            "town": town,
            "count": 50,
            "page": 0
        }

        try:
            logger.info(f"Начало парсинга вакансий SuperJob с запросом '{search_query}'")

            while True:
                try:
                    response = self.session.get(SJ_API_URL, params=params)
                    response.raise_for_status()
                    data = response.json()
                except requests.RequestException as e:
                    logger.error(f"Ошибка запроса: {e}")
                    break

                if not data.get("objects"):
                    break

                for item in data["objects"]:
                    try:
                        vacancy = Vacancy(
                            title=item.get("profession", ""),
                            company=item.get("firm_name", ""),
                            location=item.get("town", {}).get("title", ""),
                            salary=self._parse_salary(item),
                            description=item.get("candidat", ""),
                            published_at=datetime.fromtimestamp(item["date_published"]),
                            original_url=item.get("link", "")
                        )
                        vacancies.append(vacancy)
                    except (KeyError, ValueError) as e:
                        logger.error(f"Пропущена вакансия из-за ошибки в данных: {e}")

                if not data.get("more"):
                    break

                params["page"] += 1
                sleep(REQUEST_DELAY)

            logger.info(f"Парсинг SuperJob завершен. Найдено {len(vacancies)} вакансий")

        except Exception as e:
            logger.error(f"Критическая ошибка парсинга SuperJob: {e}")
        finally:
            return vacancies

    def __del__(self):
        if hasattr(self, "session"):
            self.session.close()