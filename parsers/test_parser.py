# Тест HH парсера
from job_parser.parsers.hh_parser import HHAPIParser
hh = HHAPIParser()
print(len(hh.parse_vacancies("Python")))

# Тест SJ парсера (требуется API ключ)
from job_parser.parsers.sj_parser import SJAPIParser
sj = SJAPIParser("v3.r.139040003.a8a7c7612fa80498a334a3f6d07ee655d3629be1.50b7a63c5ab8c028784ec64ca96d91c82673fa2d")
print(len(sj.parse_vacancies("Python")))

# Тест FL парсера
from job_parser.parsers.fl_parser import FLParser
fl = FLParser()
print(len(fl.parse_vacancies("Python")))