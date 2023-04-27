import mysql.connector
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

user = 'root'
password = ''
host = 'localhost'
database = 'signerpulpo'

# Configurar la conexión con la base de datos
def connect():
    config = {
        'user': user,
        'password': password,
        'host': host,
        'database': database
    }

    cnx = mysql.connector.connect(**config)

    return cnx

password_encoded = quote_plus(password)
DATABASE_URL = f"mysql+pymysql://{user}:{password_encoded}@{host}/{database}?charset=utf8mb4"

engine = create_engine(
    DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Función para crear una nueva sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()