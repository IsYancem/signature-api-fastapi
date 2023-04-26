from fastapi import HTTPException
from database import connect
from models import ArchivoFirmado, Usuario, Firma, TokenSesion, Role
from database import SessionLocal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Optional

JWT_EXP_DELTA_SECONDS = 3600 * 24  # 1 dia

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
    query = "INSERT INTO Firmas (nombre, archivo_p12, contrasena_p12, token_p12, clave_cifrado, usuario_id, fecha_caducidad) VALUES (%s, %s, %s, %s, %s, %s, %s);"
    data = (firma.nombre, firma.archivo_p12, firma.contrasena_p12, firma.token_p12, firma.clave_cifrado, firma.usuario_id, firma.fecha_caducidad)
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
def create_archivo_firmado(archivofirmado: ArchivoFirmado):
    db = SessionLocal()
    db.add(archivofirmado)
    db.commit()
    db.refresh(archivofirmado)
    db.close()

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
        query = "INSERT INTO TokensSesion (token, fecha_expiracion, usuario_id) VALUES (%s, %s, %s);"
        cursor.execute(query, (token_sesion.token, token_sesion.fecha_expiracion, token_sesion.usuario_id))
    else:
        # Si ya hay un token de sesión existente, actualizarlo
        query = "UPDATE TokensSesion SET token = %s, fecha_expiracion = %s WHERE usuario_id = %s;"
        cursor.execute(query, (token_sesion.token, token_sesion.fecha_expiracion, user_id))
        
    connection.commit()
    cursor.close()
    connection.close()

# Esta funcion obtiene firmas por id de usuario
def get_firmas_by_user_id(user_id: int):
    connection = connect()
    cursor = connection.cursor()
    firmas = []
    query = "SELECT id, nombre, fecha_caducidad FROM firmas WHERE usuario_id = %s" 
    result = cursor.execute(query, (user_id,))

    for row in cursor:  # Cambia 'result' por 'cursor'
        firmas.append({"id": row[0], "name": row[1], "fecha_caducidad": row[2]})

    return firmas

#Esta funcion elimina firmas por id 
def delete_firma_by_id(signature_id: int, user_id: int):
    connection = connect()
    cursor = connection.cursor()

    # Elimina las filas en la tabla 'archivosfirmados' que hacen referencia a la 'firma_id'
    query_delete_archivosfirmados = f"DELETE FROM ArchivosFirmados WHERE firma_id = {signature_id};"
    cursor.execute(query_delete_archivosfirmados)

    # Elimina la fila en la tabla 'Firmas'
    query_delete_firma = f"DELETE FROM Firmas WHERE id = {signature_id} AND usuario_id = {user_id};"
    cursor.execute(query_delete_firma)

    deleted_rows = cursor.rowcount
    connection.commit()
    cursor.close()
    connection.close()
    return deleted_rows

# Función para actualizar la contraseña de un usuario
def update_user_password(user_id: int, new_password: str):
    connection = connect()
    cursor = connection.cursor()
    query = f"UPDATE Usuarios SET password = '{new_password}' WHERE id = {user_id};"
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()

# Función para obtener el token de una firma por nombre y id de usuario
def get_api_token_by_name_and_user_id(name: str, user_id: int):
    connection = connect()
    cursor = connection.cursor()
    query = "SELECT token_p12 FROM Firmas WHERE nombre = %(name)s AND usuario_id = %(user_id)s;"
    cursor.execute(query, {'name': name, 'user_id': user_id})
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result

def update_api_token_by_name_and_user_id(name: str, api_key: str, user_id: int):
    connection = connect()
    cursor = connection.cursor()
    query = f"UPDATE Firmas SET token_p12 = '{api_key}' WHERE nombre = '{name}' AND usuario_id = {user_id};"
    cursor.execute(query)
    updated_rows = cursor.rowcount
    connection.commit()
    cursor.close()
    connection.close()
    return updated_rows, api_key

# Obtener informacion de un usuario por medio de su username
def get_user_by_username(username):
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT * FROM usuarios WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    cursor.close()
    cnx.close()
    return result

# Obtener el nombre de un rol a traves de id 
def get_role_name_by_id(role_id):
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT nombre FROM Roles WHERE id = %s"
    cursor.execute(query, (role_id,))
    result = cursor.fetchone()
    cursor.close()
    cnx.close()
    if result:
        return result[0]
    else:
        return None
    
# Obtener informacion de un usuario por medio de su username
def get_archivos_by_user(user_id):
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT * FROM archivosfirmados WHERE usuario_id = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    cursor.close()
    cnx.close()
    return result

# Obtener el nombre de una firma a traves de id 
def get_firma_name_by_id(firma_id):
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT nombre FROM Firmas WHERE id = %s"
    cursor.execute(query, (firma_id,))
    result = cursor.fetchone()
    cursor.close()
    cnx.close()
    if result:
        return result[0]
    else:
        return None
    
# Obtener una firma por su id
def get_firma_by_id(firma_id: int) -> Firma:
    with SessionLocal() as db:
        return db.query(Firma).filter(Firma.id == firma_id).first()

# Actualizar el nombre de una firma
def update_firma_nombre(firma_id: int, nombre: str) -> None:
    with SessionLocal() as db:
        firma = db.query(Firma).filter(Firma.id == firma_id).first()
        firma.nombre = nombre
        db.commit()