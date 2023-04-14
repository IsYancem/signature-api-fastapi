from database import connect
from models import Usuario, Firma, ArchivoFirmado, TokenSesion

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

# Servicio para agregar un token de sesión
def create_session_token(token_session: TokenSesion):
    connection = connect()
    cursor = connection.cursor()
    query = f"INSERT INTO TokensSesion (token, fecha_expiracion, usuario_id) VALUES ('{token_session.token}', '{token_session.fecha_expiracion}', {token_session.usuario_id});"
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()

# Servicio para agregar una firma
def create_firma(firma: Firma):
    connection = connect()
    cursor = connection.cursor()
    query = f"INSERT INTO Firmas (nombre, archivo_p12, contrasena_p12, token_p12, usuario_id) VALUES ('{firma.nombre}', '{firma.archivo_p12}', '{firma.contrasena_p12}', '{firma.token_p12}', {firma.usuario_id});"
    cursor.execute(query)
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
