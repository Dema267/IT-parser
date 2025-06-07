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
    filename='hh_parser.log'
)
logger = logging.getLogger(__name__)

# Константы
HH_API_URL = "https://api.hh.ru/vacancies"
REQUEST_DELAY = 0.5  # Задержка между запросами
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"


@dataclass
class Vacancy:
    title: str
    company: str
    location: str
    salary: Optional[str]
    description: str
    published_at: datetime
    source: str = "hh.ru"
    original_url: str = ""


class HHAPIParser:
    def __init__(self):
        self._init_session()

    def _init_session(self):
        """Инициализация HTTP-сессии"""
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": USER_AGENT, "Accept": "application/json"}
        )

    def _parse_salary(self, salary_data: Optional[Dict]) -> Optional[str]:
        """Форматирование данных о зарплате"""
        if not salary_data:
            return None

        salary_from = salary_data.get("from")
        salary_to = salary_data.get("to")
        currency = salary_data.get("currency", "RUR")

        parts = []
        if salary_from:
            parts.append(f"от {salary_from}")
        if salary_to:
            parts.append(f"до {salary_to}")

        return " ".join(parts) + f" {currency}" if parts else None

    def _get_vacancy_description(self, item: Dict) -> str:
        """Получение описания вакансии без дополнительного запроса"""
        snippet = item.get("snippet", {})
        requirement = snippet.get("requirement", "") or snippet.get("requirement", "")
        responsibility = snippet.get("responsibility", "")
        return f"{requirement} {responsibility}".strip()

    def parse_vacancies(
        self, search_query: str = "Python", area: int = 1
    ) -> List[Vacancy]:
        """Основной метод парсинга вакансий"""
        vacancies = []
        params = {"text": search_query, "area": area, "per_page": 50, "page": 0}

        try:
            while True:
                try:
                    response = self.session.get(HH_API_URL, params=params)
                    response.raise_for_status()
                    data = response.json()
                except requests.RequestException as e:
                    logger.error(f"Ошибка запроса: {e}")
                    break

                if not data.get("items"):
                    break

                for item in data["items"]:
                    try:
                        # Получаем alternate_url или формируем ссылку вручную по id
                        original_url = item.get("alternate_url")
                        if not original_url and "id" in item:
                            original_url = f"https://hh.ru/vacancy/{item['id']}"
                        vacancy = Vacancy(
                            title=item.get("name", ""),
                            company=item["employer"].get("name", ""),
                            location=item["area"].get("name", ""),
                            salary=self._parse_salary(item.get("salary")),
                            description=self._get_vacancy_description(item),
                            published_at=datetime.strptime(
                                item["published_at"], "%Y-%m-%dT%H:%M:%S%z"
                            ),
                            original_url=original_url or "",
                        )
                        vacancies.append(vacancy)
                    except (KeyError, ValueError) as e:
                        logger.error(f"Пропущена вакансия из-за ошибки в данных: {e}")

                if params["page"] >= data.get("pages", 1) - 1:
                    break

                params["page"] += 1
                sleep(REQUEST_DELAY)

        except Exception as e:
            logger.error(f"Критическая ошибка парсинга: {e}")
        finally:
            return vacancies

    def __del__(self):
        """Закрытие соединений при уничтожении объекта"""
        if hasattr(self, "session"):
            self.session.close()


if __name__ == "__main__":
    parser = HHAPIParser()
    vacancies = parser.parse_vacancies()
    print(f"Найдено {len(vacancies)} вакансий")