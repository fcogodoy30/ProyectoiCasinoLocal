from django.db import connections, OperationalError


def obtener_conexiones():
    local_db = connections['default']
    remote_db = connections['remote']
    return local_db, remote_db