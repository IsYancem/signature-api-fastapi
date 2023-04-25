from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from generalinfo import info_signature_route

# Gestión de Crear
from Create.registerSignature import register_signature_route
from Create.login import login_router
from Create.signup import register_route
from Create.signFile import sign_route, sign_route_api

# Gestión de Read
from Read.userInfo import userInfo_router
from Read.userSignatures import userSignatures_route
from Read.signedByUser import signed_by_user_route
from Read.showUsers import show_users_route

# Gestión de Delete
from Delete.deleteUser import delete_user_route
from Delete.removeSigned import remove_signed_route
from Delete.deleteSignature import deleteSignature_route

# Gestión de Firmados
from Firmados.sendFiles import send_files_route
from Firmados.downloadFile import download_file_route

# Gestión de Actualizar
from Update.updateUserPassword import updateUserPassword_route

from managmentPlans import get_roles_route

app = FastAPI()

# Montar la carpeta 'firmados' como ruta estática para servir los archivos XML firmados
app.mount("/firmados", StaticFiles(directory="firmados"), name="firmados")

# Endpoints
# Crear archivo firmado solo con xml, p12 y password
app.include_router(sign_route_api)


# Crear
app.include_router(sign_route) # Firmar archivos con api_key y el xml
app.include_router(register_route) # Registrar usuario
app.include_router(login_router) # Ingresar usuario
app.include_router(register_signature_route) # Registrar firma
app.include_router(info_signature_route) # Obtener informacion de firma
app.include_router(userInfo_router) # Obtener informacion de usuario
app.include_router(signed_by_user_route) # Obtener archivos firmados por usuario

# Rutas para eliminar registros - DELETE
app.include_router(remove_signed_route) # Borrar archivos firmados - Usuario
app.include_router(deleteSignature_route) # Borrar firma - Usuario

# Rutas para actualizar registros - UPDATE
app.include_router(updateUserPassword_route) # Actualizar password - Usuario
app.include_router(get_roles_route) # Actualizar Roles - Administrador

# Ruta para enviar al correo
app.include_router(send_files_route)

# Ruta para mostrar los usuarios al Admin
app.include_router(show_users_route)

# Ruta para eliminar uno o varios usuarios
app.include_router(delete_user_route)

# Ruta para descargar archivo(s) firmado(s)
app.include_router(download_file_route)

# Rutas para listar
app.include_router(userSignatures_route) # Listar firmas de un usuario

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
