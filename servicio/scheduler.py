from apscheduler.schedulers.background import BackgroundScheduler
from servicio.sync import sincronizar_desde_remota
from datetime import datetime, timedelta

def start():
    scheduler = BackgroundScheduler()

    # Obtener la hora actual
    now = datetime.now()
    print(f"La hora actual del sistema es: {now.strftime('%H:%M:%S')}")

    # Configurar las tareas para ejecutarse cada minuto
    scheduler.add_job(sincronizar_desde_remota, 'interval', minutes=15)

    scheduler.start()
    print(f"Scheduler iniciado para ejecutar la tarea cada minuto.")

if __name__ == "__main__":
    start()
