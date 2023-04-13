import mysql.connector

def get_database_connection():
    config = {
        'user': 'root',
        'password': 'admin',
        'host': 'localhost',
        'database': 'signer_pulpo'
    }

    cnx = mysql.connector.connect(**config)

    return cnx

def get_user_by_username(username):
    cnx = get_database_connection()
    cursor = cnx.cursor()
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    cursor.close()
    cnx.close()
    return result

def create_user(username, password, email):
    cnx = get_database_connection()
    cursor = cnx.cursor()
    query = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
    cursor.execute(query, (username, password, email))
    cnx.commit()
    cursor.close()
    cnx.close()

def update_user_token(username, token):
    cnx = get_database_connection()
    cursor = cnx.cursor()
    query = "UPDATE users SET token = %s WHERE username = %s"
    cursor.execute(query, (token, username))
    cnx.commit()
    cursor.close()
    cnx.close()

def get_user_by_token(token):
    cnx = get_database_connection()
    cursor = cnx.cursor()
    query = "SELECT * FROM users WHERE token = %s"
    cursor.execute(query, (token,))
    result = cursor.fetchone()
    cursor.close()
    cnx.close()
    return result

def insert_signed_file(user_id, file_name, file_path):
    cnx = get_database_connection()
    cursor = cnx.cursor()
    query = "INSERT INTO signed_files (user_id, file_name, file_path) VALUES (%s, %s, %s)"
    cursor.execute(query, (user_id, file_name, file_path))
    cnx.commit()
    cursor.close()
    cnx.close()

def get_signed_files_by_user(user_id):
    cnx = get_database_connection()
    cursor = cnx.cursor()
    query = "SELECT * FROM signed_files WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchall()
    cursor.close()
    cnx.close()
    return result

if __name__ == '__main__':
    try:
        cnx = get_database_connection()
        cnx.close()
        print('Conexión exitosa a la base de datos!')
    except Exception as e:
        print(f'Error al conectar a la base de datos: {str(e)}')