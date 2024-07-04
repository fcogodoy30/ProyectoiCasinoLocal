from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import CasinoColacion, Usuarios, Programacion
from django.contrib.auth.models import User
from .conexBD import check_nube_connection

sync_in_progress = False

# Función para sincronizar
def sincronizar_modelo(instance, using):
    if instance._syncing:
        instance.save(using=using)
        instance._syncing = False

# Función para eliminar
def eliminar_modelo(instance, using):
    model = type(instance)
    try:
        obj = model.objects.using(using).get(pk=instance.pk)
        obj.delete(using=using)
    except model.DoesNotExist:
        pass

# Sincronización para tabla CasinoColacion
@receiver(post_save, sender=CasinoColacion)
def sincronizar_casinocolacion(sender, instance, **kwargs):
    global sync_in_progress
    if sync_in_progress or instance._syncing:
        return

    try:
        sync_in_progress = True
        instance._syncing = True
        if check_nube_connection() and instance.origen == 'local':
            sincronizar_modelo(instance, 'default')
        elif check_nube_connection() and instance.origen == 'nube':
            sincronizar_modelo(instance, 'local')
    finally:
        instance._syncing = False
        sync_in_progress = False

# Eliminación registro para tabla CasinoColacion
@receiver(post_delete, sender=CasinoColacion)
def eliminar_casinocolacion(sender, instance, **kwargs):
    global sync_in_progress
    if sync_in_progress:
        return

    try:
        sync_in_progress = True
        if check_nube_connection():
            eliminar_modelo(instance, 'local')
    finally:
        sync_in_progress = False

# Sincronización para tabla Usuarios
@receiver(post_save, sender=Usuarios)
def sincronizar_Usuarios(sender, instance, **kwargs):
    global sync_in_progress
    if sync_in_progress or instance._syncing:
        return

    try:
        sync_in_progress = True
        instance._syncing = True
        if check_nube_connection() and instance.origen == 'local':
            sincronizar_modelo(instance, 'default')
        elif check_nube_connection() and instance.origen == 'nube':
            sincronizar_modelo(instance, 'local')
    finally:
        instance._syncing = False
        sync_in_progress = False

# Eliminación registro para tabla Usuarios
@receiver(post_delete, sender=Usuarios)
def eliminar_Usuarios(sender, instance, **kwargs):
    global sync_in_progress
    if sync_in_progress:
        return

    try:
        sync_in_progress = True
        if check_nube_connection():
            eliminar_modelo(instance, 'local')
    finally:
        sync_in_progress = False

# Sincronización para tabla Programacion
@receiver(post_save, sender=Programacion)
def sincronizar_Programacion(sender, instance, **kwargs):
    global sync_in_progress
    if sync_in_progress or instance._syncing:
        return

    try:
        sync_in_progress = True
        instance._syncing = True
        if check_nube_connection() and instance.origen == 'local':
            sincronizar_modelo(instance, 'default')
        elif check_nube_connection() and instance.origen == 'nube':
            sincronizar_modelo(instance, 'local')
    finally:
        instance._syncing = False
        sync_in_progress = False

# Eliminación registro para tabla Programacion
@receiver(post_delete, sender=Programacion)
def eliminar_Programacion(sender, instance, **kwargs):
    global sync_in_progress
    if sync_in_progress:
        return

    try:
        sync_in_progress = True
        if check_nube_connection():
            eliminar_modelo(instance, 'local')
    finally:
        sync_in_progress = False

# Sincronización para tabla User de Django
@receiver(post_save, sender=User)
def sincronizar_user(sender, instance, **kwargs):
    global sync_in_progress
    if sync_in_progress:
        return

    try:
        sync_in_progress = True
        if check_nube_connection():
            if instance._state.db == 'local':
                instance.save(using='default')
            elif instance._state.db == 'default':
                instance.save(using='local')
    finally:
        sync_in_progress = False

# Eliminación registro para tabla User de Django
@receiver(post_delete, sender=User)
def eliminar_user(sender, instance, **kwargs):
    global sync_in_progress
    if sync_in_progress:
        return

    try:
        sync_in_progress = True
        if check_nube_connection():
            if instance._state.db == 'local':
                User.objects.using('default').filter(pk=instance.pk).delete()
            elif instance._state.db == 'default':
                User.objects.using('local').filter(pk=instance.pk).delete()
    finally:
        sync_in_progress = False
