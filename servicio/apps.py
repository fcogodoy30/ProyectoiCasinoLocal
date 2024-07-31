from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class ServicioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'servicio'

    def ready(self):
        # Importar la función de sincronización
        from .sync import sincronizar_desde_remota
        from .scheduler import start as start_scheduler
        
        from datetime import datetime

        # Obtener la hora actual
        hora_actual = datetime.now().strftime("%H:%M:%S")
        print("La hora actual del sistema es:", hora_actual)
        
        # Ejecutar la sincronización al iniciar la aplicación
        try:
            sincronizar_desde_remota()
            logger.info('Sincronización inicial completada.')
        except Exception as e:
            logger.error(f'Error en la sincronización inicial: {str(e)}')

        # Iniciar el programador
        try:
            start_scheduler()
            logger.info('Scheduler iniciado.')
        except Exception as e:
            logger.error(f'Error al iniciar el scheduler: {str(e)}')
