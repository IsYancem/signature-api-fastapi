import os
import pymysql
import mysql.connector

# Configurar la conexión con la base de datos
def connect():
    config = {
        'user': 'root',
        'password': '45567889-123',
        'host': 'localhost',
        'database': 'FirmaDigital'
    }

    cnx = mysql.connector.connect(**config)

    return cnx