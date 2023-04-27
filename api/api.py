from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# ArchivosFirmados
from ArchivosFirmados.createArchivosFirmados import createArchivosFirmados_route
from ArchivosFirmados.deleteArchivosFirmados import deleteArchivosFirmados_route
from ArchivosFirmados.downloadArchivosFirmados import downloadArchivosFirmados_route
from ArchivosFirmados.sendArchivosFirmados import sendArchivosFirmados_route
from ArchivosFirmados.showArchivosFirmados import showArchivosFirmados_route

# Auth
from Auth.login import login_router

# Firmas
from Firmas.createFirmas import createFirmas_route
from Firmas.deleteFirmas import deleteFirmas_route
from Firmas.showFirmas import showFirmas_route
from Firmas.updateFirmas import updateFirmas_route

# Roles
from Roles.createRoles import createRoles_route
from Roles.deleteRoles import deleteRoles_route
from Roles.showRoles import showRoles_route
from Roles.updateRoles import updateRoles_route

# Usuarios
from Usuarios.createUsuarios import createUsuarios_route
from Usuarios.deleteUsuarios import deleteUsuarios_route
from Usuarios.showUsuarios import showUsuarios_route
from Usuarios.updateUsuarios import updateUsuarios_route


app = FastAPI()

# Endpoints
# Rutas de la entidad ArchivosFirmados
app.include_router(createArchivosFirmados_route)
app.include_router(deleteArchivosFirmados_route)
app.include_router(downloadArchivosFirmados_route)
app.include_router(sendArchivosFirmados_route)
app.include_router(showArchivosFirmados_route)

# Ruta de auth
app.include_router(login_router)

# Ruta de la entidad Firmas
app.include_router(createFirmas_route)
app.include_router(deleteFirmas_route)
app.include_router(showFirmas_route)
app.include_router(updateFirmas_route)

# Rutas de la entidad Roles
app.include_router(createRoles_route)
app.include_router(deleteRoles_route) 
app.include_router(showRoles_route) 
app.include_router(updateRoles_route) 

# Rutas de la entidad Usuarios
app.include_router(createUsuarios_route)
app.include_router(deleteUsuarios_route)
app.include_router(showUsuarios_route)
app.include_router(updateUsuarios_route)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)