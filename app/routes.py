from flask import Blueprint, render_template, request, jsonify
from core.database import (
    get_vacancies,
    get_vacancy_by_id,
    search_vacancies,
    get_vacancies_by_source,
    get_total_vacancies_count,
    get_unique_sources,
    get_unique_cities,
    remove_duplicates,
    get_filtered_vacancies
)
import logging
import traceback

logger = logging.getLogger(__name__)
bp = Blueprint("main", __name__)


def filter_vacancies(
    vacancies: list,
    query: str,
    location: str = "",
    company: str = "",
    salary_min: str = "",
    salary_max: str = "",
) -> list:
    """Фильтрует вакансии по запросу и другим параметрам."""
    filtered = []
    for vacancy in vacancies:
        # Проверка на соответствие запросу (в названии, компании или местоположении)
        matches_query = not query or (
            query.lower() in vacancy["title"].lower()
            or query.lower() in vacancy["company"].lower()
            or query.lower() in vacancy["location"].lower()
        )

        # Проверка на соответствие местоположению
        matches_location = (
            not location or location.lower() in vacancy["location"].lower()
        )

        # Проверка на соответствие компании
        matches_company = not company or company.lower() in vacancy["company"].lower()

        # Проверка на соответствие зарплате (если она указана)
        matches_salary = True
        if vacancy["salary"] and (salary_min or salary_max):
            try:
                # Парсим зарплату из строки
                salary_text = vacancy["salary"].lower()
                # Удаляем нечисловые символы и разделяем на части
                import re

                salary_numbers = [int(s) for s in re.findall(r"\b\d+\b", salary_text)]

                if salary_numbers:
                    # Если указана минимальная зарплата и она больше максимальной в вакансии
                    if salary_min and int(salary_min) > max(salary_numbers):
                        matches_salary = False

                    # Если указана максимальная зарплата и она меньше минимальной в вакансии
                    if salary_max and int(salary_max) < min(salary_numbers):
                        matches_salary = False
                elif salary_min or salary_max:
                    # Если в зарплате нет чисел, но указан фильтр по зарплате, считаем несоответствие
                    matches_salary = False
            except (ValueError, TypeError):
                # В случае ошибки при парсинге зарплаты и наличия фильтра, считаем несоответствие
                if salary_min or salary_max:
                    matches_salary = False

        # Если вакансия соответствует всем критериям, добавляем её в отфильтрованный список
        if matches_query and matches_location and matches_company and matches_salary:
            filtered.append(vacancy)

    return filtered


@bp.route("/")
def index():
    """Главная страница"""
    try:
        logger.debug("Начало обработки запроса главной страницы")
        # Получаем статистику для главной страницы
        stats = {
            "total_vacancies": get_total_vacancies_count(),
            "sources_count": len(get_unique_sources()),
            "cities_count": len(get_unique_cities()),
        }
        logger.debug(f"Статистика получена: {stats}")
        return render_template("index.html", stats=stats)
    except Exception as e:
        logger.error(f"Ошибка при отображении главной страницы: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return "Ошибка сервера", 500


@bp.route("/vacancies")
def vacancies():
    """Страница со списком вакансий"""
    try:
        # Получаем параметры фильтрации
        query = request.args.get('q', '')
        location = request.args.get('location', '')
        company = request.args.get('company', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        order_by = request.args.get('order_by', 'published_at')
        order_direction = request.args.get('order_direction', 'DESC')
        source = request.args.get('source', '')

        # Получаем отфильтрованные вакансии
        vacancies = get_filtered_vacancies(
            query=query,
            location=location,
            company=company,
            page=page,
            per_page=per_page,
            order_by=order_by,
            order_direction=order_direction
        )

        # Получаем общее количество вакансий для пагинации
        total_count = get_total_vacancies_count(query, location, company)
        total_pages = (total_count + per_page - 1) // per_page

        # Получаем списки для фильтров
        sources = get_unique_sources()
        cities = get_unique_cities()

        return render_template(
            'vacancies.html',
            vacancies=vacancies,
            query=query,
            location=location,
            company=company,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            total_count=total_count,
            sources=sources,
            cities=cities,
            current_source=source
        )
    except Exception as e:
        logger.error(f"Ошибка при отображении списка вакансий: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return "Ошибка сервера", 500


@bp.route("/search")
def search():
    """Поиск вакансий"""
    try:
        query = request.args.get('q', '')
        if query:
            results = search_vacancies(query)
        else:
            results = get_vacancies()
        return render_template('vacancies.html', vacancies=results)
    except Exception as e:
        logger.error(f"Ошибка при поиске вакансий: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return "Ошибка сервера", 500


@bp.route("/vacancy/<int:vacancy_id>")
def vacancy_detail(vacancy_id):
    """Детальная информация о вакансии"""
    try:
        vacancy = get_vacancy_by_id(vacancy_id)
        if vacancy:
            return render_template('vacancy_detail.html', vacancy=vacancy)
        return "Вакансия не найдена", 404
    except Exception as e:
        logger.error(f"Ошибка при отображении деталей вакансии {vacancy_id}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return "Ошибка сервера", 500


@bp.route("/api/vacancies")
def api_vacancies():
    """API endpoint для получения списка вакансий"""
    try:
        query = request.args.get('q', '')
        location = request.args.get('location', '')
        company = request.args.get('company', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))

        vacancies = get_filtered_vacancies(
            query=query,
            location=location,
            company=company,
            page=page,
            per_page=per_page
        )

        return jsonify({
            'status': 'success',
            'data': vacancies,
            'total': get_total_vacancies_count(query, location, company)
        })
    except Exception as e:
        logger.error(f"Ошибка в API /api/vacancies: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@bp.route("/api/vacancy/<int:vacancy_id>")
def api_vacancy_detail(vacancy_id):
    """API endpoint для получения деталей вакансии"""
    try:
        vacancy = get_vacancy_by_id(vacancy_id)
        if vacancy:
            return jsonify({
                'status': 'success',
                'data': vacancy
            })
        return jsonify({
            'status': 'error',
            'message': 'Vacancy not found'
        }), 404
    except Exception as e:
        logger.error(f"Ошибка в API /api/vacancy/{vacancy_id}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500