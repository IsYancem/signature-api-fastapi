from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from dependencies import get_current_user
from database2 import SessionLocal
from models import Usuario, TokenSesion
from sqlalchemy.orm import Session

delete_user_route = APIRouter()

def delete_users(db: Session, user_ids: List[int]):
    for user_id in user_ids:
        # Verificar si el usuario existe
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail=f"El usuario con id {user_id} no existe")

        # Eliminar el usuario y sus registros relacionados en cascada
        db.delete(user)
        db.commit()

@delete_user_route.post("/deleteUser")
async def delete_user(user_ids: List[int], current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado, no existe el usuario activo")

    if current_user["role_id"] != 1:
        raise HTTPException(status_code=403, detail="No tiene permisos para realizar esta acción")

    db = SessionLocal()
    try:
        delete_users(db, user_ids)
        return {"message": f"Los usuarios con IDs {user_ids} han sido eliminados exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar usuarios: {str(e)}")
    finally:
        db.close()
