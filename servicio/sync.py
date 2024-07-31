from datetime import datetime, timedelta
import logging
from django.db import connections, OperationalError
from django.contrib.auth.models import User
from .models import Usuarios, CasinoColacion, Programacion

logger = logging.getLogger(__name__)

# CAMPO FECHA GLOBAL
now = datetime.now()

def obtener_conexiones():
    local_db = connections['default']
    remote_db = connections['remote']
    return local_db, remote_db

def cerrar_conexiones():
    for conn in connections.all():
        conn.close()

def verificar_conexiones():
    try:
        local_db, remote_db = obtener_conexiones()
        with remote_db.cursor() as cursor:
            cursor.execute("SELECT 1")
        with local_db.cursor() as cursor:
            cursor.execute("SELECT 1")
        logger.info('Conexiones a las bases de datos verificadas.')
        return True
    except OperationalError as e:
        logger.error('Error de conexión: %s', str(e))
        return False
    except Exception as e:
        logger.error('Error inesperado en la verificación de conexiones: %s', str(e))
        return False

#Funsion para llamar todas las funciones
def sincronizar_desde_remota():
    if not verificar_conexiones():
        logger.error('No se pudo establecer conexión con una o ambas bases de datos.')
        return
    try:
        logger.info('Iniciando sincronización desde la fuente remota...')
        
        sincronizar_tab_user_usuarios(User, Usuarios, 'auth_user', 'servicio_usuarios')
        sincronizar_tab_menu(CasinoColacion, 'servicio_casinocolacion')
        sincronizar_tab_programacion(Programacion, 'servicio_programacion')
        
        logger.info('Sincronización completada.')
        
    except Exception as e:
        logger.error('Error en sincronizar_desde_remota: %s', str(e))

#==============================================================
# ======= SINCRONIZACION TABLAS USER Y USUARIOS ===============
#==============================================================
def sincronizar_tab_user_usuarios(mod_user, mod_usuario, tab_user, tab_usuario):
    try:
        local_db, remote_db = obtener_conexiones()
        logger.info(f'Sincronizando tablas user y usuario desde remota a local.')
        with remote_db.cursor() as remote_cursor:
            # Obtener datos de la tabla User del Servidor Nube
            remote_cursor.execute(f"SELECT id, password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined FROM {tab_user}")
            user_remote = remote_cursor.fetchall()

            for row in user_remote:
                excluir_campos = ['id', 'last_login'] #excluir campos
                columns = [field.name for field in mod_user._meta.fields if field.name not in excluir_campos]
                values = row[1:]

                # Obtener datos de la tabla Usuarios del Servidor Nube
                remote_cursor.execute(f"SELECT id, rut, nombre, apellido, activo, _syncing, origen, tipo_usuario_id  FROM {tab_usuario} WHERE rut = '{row[3]}'")
                usua_remote = remote_cursor.fetchall()

                for usu in usua_remote:
                    excluir = ['id','id_user','Id_tabSync','tipo_usuario'] #excluir campos
                    columnsUsuario = [field.name for field in mod_usuario._meta.fields if field.name not in excluir]
                    valueusuario = usu[1:]

                    valida = mod_user.objects.filter(username=row[3])
                    with local_db.cursor() as local_cursor:
                        if valida.exists():  # Validar si existe el registro
                            # Actualizar tabla User
                            update_query = f"""
                                UPDATE {tab_user}
                                SET {', '.join(f'{col} = %s' for col in columns)}
                                WHERE username = %s
                            """
                            # Concatenar las tuplas y ejecutar la consulta
                            local_cursor.execute(update_query, tuple(values) + (row[3],))

                            # Actualizar tabla Usuarios
                            update_query = f"""
                                UPDATE {tab_usuario}
                                SET {', '.join(f'{col} = %s' for col in columnsUsuario)}, tipo_usuario_id = %s
                                WHERE rut = %s
                            """
                            local_cursor.execute(update_query, tuple(valueusuario) + (usu[1],))
                            logger.info(f'Registro actualizado en {tab_user} local: username={row[3]}')

                        else:
                            # Insertar nuevo registro en la tabla User
                            insert_query = f"""
                                INSERT INTO {tab_user} ({', '.join(columns)})
                                VALUES ({', '.join('%s' for _ in columns)})
                            """
                            local_cursor.execute(insert_query, tuple(values))
                            
                            # Obtener el Id ingresado para insertarlo en el campo relacionado con User
                            username = row[3]  # Suponiendo que el username está en la cuarta posición de la fila
                            mod_user_id = mod_user.objects.get(username=username).id

                            insert_query = f"""
                                INSERT INTO {tab_usuario} ({', '.join(columnsUsuario)},tipo_usuario_id, id_user_id ,Id_tabSync)
                                VALUES ({', '.join('%s' for _ in columnsUsuario)}, %s, %s, %s) 
                            """
                            local_cursor.execute(insert_query, tuple(valueusuario) + (mod_user_id, usu[0]))
                            logger.info(f'Nuevo registro insertado en tabla User y Usuarios')
    except Exception as e:
        logger.error(f'Error en sincronizar_tab_user_usuarios: {str(e)}')
    finally:
        cerrar_conexiones()

#==============================================================
# ======= SINCRONIZACION TABLA CASINO COLACION  ===============
#==============================================================

def sincronizar_tab_menu(mod_casinocolacion,tab_casinocolacion):
    try:
        local_db, remote_db = obtener_conexiones()
        logger.info(f'Sincronizando tabla colacion menu semanal.')
        with remote_db.cursor() as remote_cursor:
            # Obtener datos de la tabla User del Servidor Nube
            remote_cursor.execute(f"SELECT id,titulo,descripcion,fecha_servicio,id_estado,_syncing,origen,id_opciones_id FROM {tab_casinocolacion}")
            
            CasinoColacion_remote = remote_cursor.fetchall()
            
            for row in CasinoColacion_remote:
                
                excluir_campos = ['id', 'Id_tabSync','id_opciones','fecha_actualizacion'] #excluir campos
                columns = [field.name for field in mod_casinocolacion._meta.fields if field.name not in excluir_campos]
                
                values = row[1:]
                
                #Validamos si existe registro
                valida = mod_casinocolacion.objects.filter(Id_tabSync=row[0])
                with local_db.cursor() as local_cursor:
                        if valida.exists():  # Validar si existe el registro
                            # Actualizar tabla User
                            update_query = f"""
                                UPDATE {tab_casinocolacion}
                                SET {', '.join(f'{col} = %s' for col in columns)} , id_opciones_id = %s, fecha_actualizacion = %s
                                WHERE Id_tabSync = %s
                            """
                            # Concatenar las tuplas y ejecutar la consulta
                            local_cursor.execute(update_query,  tuple(values) + (now,row[0],))
                            logger.info(f'Registro actualizado en tabla colacion menu semanal')
                        else:
                            # Insertar nuevo registro en la tabla User
                            insert_query = f"""
                                INSERT INTO {tab_casinocolacion} ({', '.join(columns)}, id_opciones_id, fecha_actualizacion, Id_tabSync)
                                VALUES ({', '.join('%s' for _ in columns)}, %s, %s, %s)
                            """
                            local_cursor.execute(insert_query, tuple(values) + (now, row[0],))
                            logger.info(f'Registro Igresado a tabla CasinoCoalcion')                
    except Exception as e:
        logger.error(f'Error en sincronizar_tab_menu: {str(e)}')
    finally:
        cerrar_conexiones()
        
#==============================================================
# =======   SINCRONIZACION TABLA PROGRAMACION   ===============
#==============================================================

# DIAS DE LA SEMANA SEGUN CALENDARIO EN CURSO DE MENU
def diaDeSemana():
    # Obtener la fecha actual
    fechaActual = datetime.now().date()
    # Calcular el inicio de la semana actual (lunes)
    inicioSem = fechaActual - timedelta(days=fechaActual.weekday())
    # Calcular el inicio y fin de la siguiente semana (lunes a viernes)
    inicioSemSiguiente = inicioSem + timedelta(days=7)
    finSemSiguiente = inicioSemSiguiente + timedelta(days=4)
    
    return inicioSemSiguiente, finSemSiguiente

# FUNCION PARA SINCRONIZAR 
def sincronizar_tab_programacion(mod_programacion, tab_programacion):
    try:
        local_db, remote_db = obtener_conexiones()
        logger.info(f'Sincronizando tabla colacion menu semanal.')
        iniSem, finSem = diaDeSemana()
        # Se obtiene los datos de la tabla programacion en la nube
        with remote_db.cursor() as remote_cursor:
            sql_query = f"""
            SELECT id, menu_id, nom_menu, fecha_servicio, cantidad_almuerzo, impreso, fecha_impreso, fecha_seleccion, _syncing, origen, usuario_id, Id_tabSync 
            FROM {tab_programacion} 
            WHERE origen = 'nube' and fecha_servicio BETWEEN %s AND %s 
            """
            remote_cursor.execute(sql_query, (iniSem, finSem))
            programacion_remote = remote_cursor.fetchall()

            for row_data_pro in programacion_remote:
                with local_db.cursor() as local_cursor:
                    # Obtener el id de la tabla usuarios de la nube
                    query = f"""SELECT id FROM servicio_usuarios where Id_tabSync = {row_data_pro[10]} """
                    local_cursor.execute(query)
                    result = local_cursor.fetchone()
                    if result:
                        id_usua_local = result[0]
                    else:
                        continue  # Si no se encuentra el usuario, continuar con el siguiente registro

                    # Consultar las programaciones del usuario para la semana
                    valida = Programacion.objects.filter(
                        usuario__id=id_usua_local,
                        fecha_servicio=row_data_pro[3]  # Validar por fecha de servicio exacta
                    )

                    if not valida.exists():
                        # Filtro por el id_menu de la tabla programacion de la nube
                        query = f"""SELECT id, titulo, fecha_servicio, origen, id_opciones_id FROM servicio_casinocolacion where Id_tabSync = {row_data_pro[1]} """
                        local_cursor.execute(query)
                        menu_local = local_cursor.fetchone()

                        if menu_local:
                            excluir = ['id', 'usuario', 'cantidad_almuerzo', '_syncing', 'impreso', 'fecha_impreso', 'fecha_seleccion', 'Id_tabSync']  # excluir campos
                            menu_columns = [field.name for field in mod_programacion._meta.fields if field.name not in excluir]
                            menu_data = menu_local[:4]

                            insert_query = f"""
                                INSERT INTO servicio_programacion ({', '.join(menu_columns)}, cantidad_almuerzo, fecha_seleccion, Id_tabSync, _syncing, impreso, fecha_impreso, usuario_id)
                                VALUES ({', '.join('%s' for _ in menu_columns)}, %s, %s, %s, %s, %s, %s, %s)
                            """
                            local_cursor.execute(insert_query, tuple(menu_data) + (row_data_pro[4], row_data_pro[7], row_data_pro[0], row_data_pro[8], row_data_pro[5], row_data_pro[6], id_usua_local))
                            logger.info(f'Nuevo registro insertado en tabla Programacion')

    except Exception as e:
        logger.error(f'Error en sincronizar_tab_programacion: {str(e)}')
    finally:
        cerrar_conexiones()