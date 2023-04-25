from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from dependencies import get_current_user
from database2 import SessionLocal
from models2 import Usuario, Role
from datetime import datetime
from sqlalchemy.orm import Session

#Todo esto es para obtener todos los roles de los usuarios
get_roles_route = APIRouter()

def get_roles(db: Session):
    roles = db.query(Role).all()
    return roles

@get_roles_route.get("/roles")
async def get_all_roles(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado, no existe el usuario activo")

    if current_user["role_id"] != 1:
        raise HTTPException(status_code=403, detail="No tiene permisos para realizar esta acción")

    db = SessionLocal()
    try:
        roles = get_roles(db)
        return roles
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener roles: {str(e)}")
    finally:
        db.close()

#Todo esto es para actualizar el rol de un usuario
update_role_route = APIRouter()

class UpdateUserRole(BaseModel):
    user_id: int
    role_id: int

def update_user_role_in_db(db: Session, user_id: int, role_id: int):
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail=f"El usuario con id {user_id} no existe")

    user.role_id = role_id
    db.commit()

@update_role_route.put("/updateUserRole")
async def update_user_role_route(update_user_role: UpdateUserRole, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado, no existe el usuario activo")

    if current_user["role_id"] != 1:
        raise HTTPException(status_code=403, detail="No tiene permisos para realizar esta acción")

    db = SessionLocal()
    try:
        update_user_role_in_db(db, update_user_role.user_id, update_user_role.role_id)
        return {"message": f"El rol del usuario con ID {update_user_role.user_id} ha sido actualizado a {update_user_role.role_id}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar el rol del usuario: {str(e)}")
    finally:
        db.close()

