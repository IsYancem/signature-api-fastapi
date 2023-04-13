from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, SignedFile
from passlib.context import CryptContext

# Crear la conexión a la base de datos
engine = create_engine('mysql+mysqlconnector://root:admin@localhost/signer_pulpo')
Session = sessionmaker(bind=engine)

# Crear la tabla si no existe
Base.metadata.create_all(engine)

# Crear una sesión de la base de datos
session = Session()

# Crear un usuario
username = 'user12'
password = 'password12'
email = 'user12@example.com'
hashed_password = CryptContext(schemes=["bcrypt"]).hash(password)
user = User(username=username, password=hashed_password, email=email)

# Agregar el usuario a la base de datos
session.add(user)
session.commit()

# Recuperar el usuario
user = session.query(User).filter_by(username=username).first()
print(user)

# Agregar un archivo firmado
nombre_archivo = 'archivo.txt'
ruta_archivo = '/firmados/archivo.txt'
signed_file = SignedFile(user_id=user.id, file_name=nombre_archivo, file_path=ruta_archivo)
session.add(signed_file)
session.commit()

# Recuperar los archivos firmados del usuario
signed_files = user.signed_files
print(signed_files)