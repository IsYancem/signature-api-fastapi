from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from signFile import sign_route
from signup import register_route
from login import login_router
from registerSignature import register_signature_route
from generalinfo import info_signature_route

app = FastAPI()

# Montar la carpeta 'firmados' como ruta estática para servir los archivos XML firmados
app.mount("/firmados", StaticFiles(directory="firmados"), name="firmados")

# Aqui estan las rutas para los endpoints
app.include_router(sign_route)
app.include_router(register_route)
app.include_router(login_router)
app.include_router(register_signature_route)
app.include_router(info_signature_route)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
