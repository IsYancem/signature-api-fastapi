import os
import pymysql
import mysql.connector

# Configurar la conexión con la base de datos
def connect():
    config = {
        'user': 'root',
        'password': 'admin',
        'host': 'localhost',
        'database': 'signerpulpo'
    }

    cnx = mysql.connector.connect(**config)

    return cnx