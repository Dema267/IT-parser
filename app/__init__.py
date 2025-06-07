# Flask app initialization
from flask import Flask
from .routes import bp
import logging
import sys

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def create_app():
    """Создает и настраивает Flask приложение"""
    try:
        app = Flask(__name__)

        # Регистрируем blueprint
        app.register_blueprint(bp)

        logger.info("Flask приложение успешно создано")
        return app
    except Exception as e:
        logger.error(f"Ошибка при создании Flask приложения: {e}")
        raise