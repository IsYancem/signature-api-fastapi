from database import connect
from models import Usuario, Firma, ArchivoFirmado, TokenSesion
from datetime import datetime, timedelta
import base64
import io


JWT_EXP_DELTA_SECONDS = 3600*24  # 1 hora


# Servicio para agregar un usuario
def create_user(user: Usuario):
    connection = connect()
    cursor = connection.cursor()
    query = f"INSERT INTO Usuarios (username, password, correo, estado, role_id) VALUES ('{user.username}', '{user.password}', '{user.correo}', {user.estado}, {user.role_id});"
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()

# Servicio para obtener un usuario por su correo o username
def get_user_by_email_or_username(email: str, username: str):
    connection = connect()
    cursor = connection.cursor()
    query = f"SELECT * FROM Usuarios WHERE correo = '{email}' OR username = '{username}';"
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result


def create_firma(firma: Firma):
    connection = connect()
    cursor = connection.cursor()

    # Insertar la firma en la base de datos usando la cadena base64
    query = "INSERT INTO Firmas (nombre, archivo_p12, contrasena_p12, token_p12, usuario_id) VALUES (%s, %s, %s, %s, %s);"
    data = (firma.nombre, firma.archivo_p12, firma.contrasena_p12, firma.token_p12, firma.usuario_id)
    cursor.execute(query, data)

    connection.commit()
    cursor.close()
    connection.close()

# Servicio para obtener las firmas de un usuario
def get_firmas_by_user(user_id: int):
    connection = connect()
    cursor = connection.cursor()
    query = f"SELECT * FROM Firmas WHERE usuario_id = {user_id};"
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

# Servicio para agregar un archivo firmado
def create_archivo_firmado(archivo_firmado: ArchivoFirmado):
    connection = connect()
    cursor = connection.cursor()
    query = f"INSERT INTO ArchivosFirmados (nombre_archivo, fecha_hora_firma, firma_id, usuario_id) VALUES ('{archivo_firmado.nombre_archivo}', '{archivo_firmado.fecha_hora_firma}', {archivo_firmado.firma_id}, {archivo_firmado.usuario_id});"
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()

# Servicio para obtener los archivos firmados de un usuario
def get_archivos_firmados_by_user(user_id: int):
    connection = connect()
    cursor = connection.cursor()
    query = f"SELECT * FROM ArchivosFirmados WHERE usuario_id = {user_id};"
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

def get_user_by_username(username):
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT * FROM usuarios WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    cursor.close()
    cnx.close()
    return result

def get_user_by_email(email):
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT * FROM usuarios WHERE correo = %s"
    cursor.execute(query, (email,))
    result = cursor.fetchone()
    cursor.close()
    cnx.close()
    return result

def get_session_token_by_user_id(user_id: int):
    connection = connect()
    cursor = connection.cursor()
    query = f"SELECT * FROM TokensSesion WHERE usuario_id = {user_id};"
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result

# Servicio para agregar un token de sesión o actualizarlo si ya existe
def create_or_update_session_token(user_id: int, token: str):
    connection = connect()
    cursor = connection.cursor()

    # Buscar el token de sesión actual del usuario
    query = f"SELECT * FROM TokensSesion WHERE usuario_id = {user_id};"
    cursor.execute(query)
    result = cursor.fetchone()
    token_sesion = TokenSesion(token=token, fecha_expiracion=str(datetime.now() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)), usuario_id=user_id)

    if result is None:
        # Si no hay un token de sesión existente, crear uno nuevo
        query = f"INSERT INTO TokensSesion (token, fecha_expiracion, usuario_id) VALUES ('{token_sesion.token}', '{token_sesion.fecha_expiracion}', {token_sesion.usuario_id});"
        cursor.execute(query)
    else:
        # Si ya hay un token de sesión existente, actualizarlo
        query = f"UPDATE TokensSesion SET token = '{token_sesion.token}', fecha_expiracion='{token_sesion.fecha_expiracion}'  WHERE usuario_id = {user_id};"
        cursor.execute(query)

    connection.commit()
    cursor.close()
    connection.close()

    # Añade esta función a tu archivo services.py
def get_firmas_by_user_id(user_id: int):
    connection = connect()
    cursor = connection.cursor()
    firmas = []
    query = "SELECT id, nombre FROM firmas WHERE usuario_id = %s" 
    result = cursor.execute(query, (user_id,))

    for row in cursor:  # Cambia 'result' por 'cursor'
        firmas.append({"id": row[0], "name": row[1]})

    return firmas
