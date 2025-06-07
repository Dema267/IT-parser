import requests
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
import sqlite3
from time import sleep

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
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._init_session()
        self._init_db()

    def _init_session(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "X-Api-App-Id": self.api_key,
            "Accept": "application/json"
        })

    def _init_db(self):
        self.conn = sqlite3.connect("vacancies.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute("""
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
        self.conn.commit()

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

    def _save_vacancy(self, vacancy: Vacancy):
        try:
            self.cursor.execute("""
                INSERT OR IGNORE INTO vacancies (
                    title, company, location, salary, 
                    description, published_at, source, original_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                vacancy.title,
                vacancy.company,
                vacancy.location,
                vacancy.salary,
                vacancy.description,
                vacancy.published_at.isoformat(),
                vacancy.source,
                vacancy.original_url,
            ))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка сохранения в БД: {e}")

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
            while True:
                try:
                    response = self.session.get(SJ_API_URL, params=params)
                    response.raise_for_status()
                    data = response.json()
                except requests.RequestException as e:
                    print(f"Ошибка запроса: {e}")
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
                        self._save_vacancy(vacancy)
                    except (KeyError, ValueError) as e:
                        print(f"Пропущена вакансия из-за ошибки в данных: {e}")

                if not data.get("more"):
                    break

                params["page"] += 1
                sleep(REQUEST_DELAY)

        except Exception as e:
            print(f"Критическая ошибка парсинга: {e}")
        finally:
            return vacancies

    def __del__(self):
        if hasattr(self, "session"):
            self.session.close()
        if hasattr(self, "conn"):
            self.conn.close()