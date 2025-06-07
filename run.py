from app import create_app
from core.scheduler import start_scheduler
import threading


app = create_app()

if __name__ == '__main__':

    # Запускаем планировщик в отдельном потоке
    scheduler_thread = threading.Thread(target=start_scheduler)
    scheduler_thread.start()

    app.run(debug=False)