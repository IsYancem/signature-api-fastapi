from fastapi import APIRouter, Depends, HTTPException, status
from dependencies import get_current_user
from database import SessionLocal
from models import Usuario, Role, UsuarioInfo
from services import get_user_by_username, get_role_name_by_id

showUsuarios_route = APIRouter()


# Mostrar la informacion de los Usuarios - Admin
@showUsuarios_route.get("/showUsers")
async def show_users(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado, no existe el usuario activo")
    if current_user["role_id"] != 1:
        raise HTTPException(status_code=403, detail="No autorizado, no tiene permisos suficientes")

    db = SessionLocal()
    usuarios = db.query(Usuario.id,Usuario.username, Usuario.correo, Usuario.estado, Role.nombre).join(Role).all()

    usuarios_list = []
    for usuario in usuarios:
        usuarios_list.append({"id": usuario[0], "username": usuario[1], "correo": usuario[2], "estado": "activo" if usuario[3] else "inactivo", "rol": usuario[4]})

    return {"usuarios": usuarios_list}


# Mostrar la informacion de Usuarios - Usuario 
@showUsuarios_route.get("/user-info", response_model=UsuarioInfo)
async def get_user_info(current_user: dict = Depends(get_current_user)):
    user = get_user_by_username(current_user["username"])
    role_name = get_role_name_by_id(user[5])
    user_info = UsuarioInfo(
        username=user[1],
        correo=user[3],
        nombre_rol=role_name
    )
    return user_info
