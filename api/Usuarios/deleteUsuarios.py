from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from pydantic import BaseModel
from dependencies import get_current_user
from database import SessionLocal, get_db
from models import Usuario, TokenSesion, ArchivoFirmado, Firma
from sqlalchemy.orm import Session
from schemas import DeleteResponse


deleteUsuarios_route = APIRouter()

def delete_users(db: Session, user_ids: List[int]):
    for user_id in user_ids:
        # Verificar si el usuario existe
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail=f"El usuario con id {user_id} no existe")

        # Eliminar los registros relacionados en cascada en la tabla "ArchivosFirmados"
        db.query(ArchivoFirmado).filter(ArchivoFirmado.usuario_id == user_id).delete(synchronize_session=False)
        db.query(Firma).filter(Firma.usuario_id == user_id).delete(synchronize_session=False)
        db.query(TokenSesion).filter(TokenSesion.usuario_id == user_id).delete(synchronize_session=False)

        # Eliminar el usuario y sus registros relacionados en cascada
        db.delete(user)
        db.commit()

class DeleteUser(BaseModel):
    user_ids: List[int]


# Eliminar Usuario del sistema - Admin
@deleteUsuarios_route.post("/deleteUser")
async def delete_user(delete_user: DeleteUser, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado, no existe el usuario activo")

    if current_user["role_id"] != 1:
        raise HTTPException(status_code=403, detail="No tiene permisos para realizar esta acción")

    db = SessionLocal()
    try:
        delete_users(db, delete_user.user_ids)
        return {"message": f"Los usuarios con IDs {delete_user.user_ids} han sido eliminados exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar usuarios: {str(e)}")
    finally:
        db.close()


# Eliminar cuenta de Usuario - Usuario
@deleteUsuarios_route.delete("/usuario/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user or current_user["id"] != user_id:
        raise HTTPException(status_code=401, detail="No autorizado")

    user = db.query(Usuario).filter(Usuario.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="El usuario no existe")

    db.query(ArchivoFirmado).filter(ArchivoFirmado.usuario_id == user_id).delete(synchronize_session=False)
    db.query(Firma).filter(Firma.usuario_id == user_id).delete(synchronize_session=False)
    db.query(TokenSesion).filter(TokenSesion.usuario_id == user_id).delete(synchronize_session=False)
    
    db.delete(user)
    db.commit()

    return DeleteResponse(message="Usuario eliminado exitosamente")
