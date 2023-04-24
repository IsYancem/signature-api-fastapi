from fastapi import APIRouter, Depends, HTTPException, status
from dependencies import get_current_user
from database2 import SessionLocal
from models2 import Usuario, Role

show_users_route = APIRouter()

@show_users_route.get("/showUsers")
async def show_users(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado, no existe el usuario activo")
    if current_user["role_id"] != 1:
        raise HTTPException(status_code=403, detail="No autorizado, no tiene permisos suficientes")

    db = SessionLocal()
    usuarios = db.query(Usuario.username, Usuario.correo, Usuario.estado, Role.nombre).join(Role).all()

    usuarios_list = []
    for usuario in usuarios:
        usuarios_list.append({"username": usuario[0], "correo": usuario[1], "estado": "activo" if usuario[2] else "inactivo", "rol": usuario[3]})

    return {"usuarios": usuarios_list}
