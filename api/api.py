from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from login import login_router  
from register import register_router
from digitalSignature import sign_route 

app = FastAPI()

# Montar la carpeta 'firmados' como ruta estática para servir los archivos XML firmados
app.mount("/firmados", StaticFiles(directory="firmados"), name="firmados")

#Aqui esta la ruta para el endpoint /login
app.include_router(login_router)

#Aqui esta la ruta para el endpoint /register
app.include_router(register_router)

#Aqui esta la ruta para el endpoint /sign-xml
app.include_router(sign_route)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
