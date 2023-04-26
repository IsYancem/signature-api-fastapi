from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
# JWToken
from generalinfo import info_signature_route
# Crear
from Create.signup import register_route
from Create.login import login_router
from Create.registerSignature import register_signature_route
from Create.signFile import sign_route, sign_route_api
# Read o Mostrar
from Read.userInfo import userInfo_router
from Read.signedByUser import signed_by_user_route
from Read.showUsers import show_users_route
from Read.userSignatures import userSignatures_route
# Delete
from Delete.deleteUser import delete_user_route
from Delete.removeSigned import remove_signed_route
from Delete.deleteSignature import deleteSignature_route
# Firmados
from firmados.sendFiles import send_files_route
from firmados.downloadFile import download_file_route
# Actualizar
from managmentPlans import get_roles_route, update_role_route
from Update.updateUserPassword import updateUserPassword_route

app = FastAPI()

# Montar la carpeta 'firmados' como ruta estática para servir los archivos XML firmados
app.mount("/firmados", StaticFiles(directory="firmados"), name="firmados")

# Endpoints
# Crear archivo firmado solo con xml, p12 y password
app.include_router(sign_route_api)

# Rutas para Crear registros
app.include_router(sign_route) # Firmar archivos con api_key y el xml
app.include_router(register_route) # Registrar usuario
app.include_router(login_router) # Ingresar usuario
app.include_router(register_signature_route) # Registrar firma
app.include_router(info_signature_route) # Obtener informacion de firma
app.include_router(userInfo_router) # Obtener informacion de usuario
app.include_router(signed_by_user_route) # Obtener archivos firmados por usuario

# Rutas para Actualizar registros
app.include_router(update_role_route) # Actualizar el rol del usuario - Admin
app.include_router(updateUserPassword_route) # Actualizar contraseña - Usuario

# Rutas para Eliminar registros
app.include_router(remove_signed_route) # Eliminar archivo firmado - Usuario
app.include_router(deleteSignature_route) # Eliminar firmas - Usuario
app.include_router(delete_user_route) # Eliminar uno o varios usuarios - Admin

# Rutas para Mostrar registros
app.include_router(get_roles_route) # Mostrar los roles de usuario - Admin
app.include_router(show_users_route) # Mostrar los usuarios existentes - Admin
app.include_router(download_file_route) # Descargar archivo(s) firmado(s) - Usuario
app.include_router(send_files_route) # Enviar archivo(s) firmado(s) al correo - Usuario
app.include_router(userSignatures_route) # Mostrar las firmas de un usuario - Usuario

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)