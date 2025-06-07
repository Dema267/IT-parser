from app import create_app
from core.scheduler import start_scheduler
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log'
)
logger = logging.getLogger(__name__)

app = create_app()
scheduler = start_scheduler()

if __name__ == "__main__":
    logger.info("Запуск приложения...")
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        logger.error(f"Ошибка при запуске приложения: {e}")