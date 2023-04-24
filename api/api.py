from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from signFile import sign_route
from signup import register_route
from login import login_router
from registerSignature import register_signature_route
from generalinfo import info_signature_route
from Read.userInfo import userInfo_router
from Read.signedByUser import signed_by_user_route
from Delete.removeSigned import remove_signed_route
from firmados.sendFiles import send_files_route
from Read.showUsers import show_users_route
from Delete.deleteUser import delete_user_route

app = FastAPI()

# Montar la carpeta 'firmados' como ruta estática para servir los archivos XML firmados
app.mount("/firmados", StaticFiles(directory="firmados"), name="firmados")

# Aqui estan las rutas para los endpoints
app.include_router(sign_route)
app.include_router(register_route)
app.include_router(login_router)
app.include_router(register_signature_route)
app.include_router(info_signature_route)
app.include_router(userInfo_router)
app.include_router(signed_by_user_route)

# Rutas para eliminar registros
app.include_router(remove_signed_route)

# Ruta para enviar al correo
app.include_router(send_files_route)

# Ruta para mostrar los usuarios al Admin
app.include_router(show_users_route)

# Ruta para eliminar uno o varios usuarios
app.include_router(delete_user_route)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
