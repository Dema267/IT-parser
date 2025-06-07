from parsers.hh_parser import parse_hh
from parsers.superjob_parser import parse_superjob
from metrics.logger import save_metrics
import time

def run_all_parsers():
    total_vacancies = 0
    total_errors = 0
    salary_total = 0
    salary_with_data = 0
    start = time.time()

    # HH
    hh_vacancies = parse_hh()
    total_vacancies += len(hh_vacancies)
    salary_with_data += sum(1 for v in hh_vacancies if v.get("salary"))
    salary_total += len(hh_vacancies)

    # SuperJob
    sj_vacancies = parse_superjob()
    total_vacancies += len(sj_vacancies)
    salary_with_data += sum(1 for v in sj_vacancies if v.get("salary"))
    salary_total += len(sj_vacancies)

    # Метрики
    parsing_time = round(time.time() - start, 2)
    salary_percent = round(salary_with_data / salary_total * 100, 2) if salary_total else 0

    save_metrics(
        source='all',
        vacancies_count=total_vacancies,
        parsing_time=parsing_time,
        salary_percent=salary_percent,
        error_count=total_errors,
        comment='Общий парсинг hh.ru + superjob'
    )
