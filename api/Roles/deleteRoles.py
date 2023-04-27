from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_current_user
from database import get_db
from models import Role, Usuario, Firma, ArchivoFirmado, TokenSesion

deleteRoles_route = APIRouter()

@deleteRoles_route.delete("/roles/{rol_id}", status_code=status.HTTP_200_OK)
async def delete_rol(
    rol_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user or current_user["role_id"] != 1:
        raise HTTPException(status_code=401, detail="No autorizado")

    rol = db.query(Role).filter(Role.id == rol_id).first()
    if not rol:
        raise HTTPException(status_code=404, detail="El rol no existe")

    # Obtener todos los usuarios con el rol a eliminar
    usuarios = db.query(Usuario).filter(Usuario.role_id == rol_id).all()

    # Eliminar todos los usuarios y firmas relacionados con el rol a eliminar
    for usuario in usuarios:
        db.query(ArchivoFirmado).filter(ArchivoFirmado.usuario_id == usuario.id).delete()
        db.query(Firma).filter(Firma.usuario_id == usuario.id).delete()
        db.query(TokenSesion).filter(TokenSesion.usuario_id == usuario.id).delete()
        db.query(Usuario).filter(Usuario.id == usuario.id).delete()

    # Eliminar el rol
    db.query(Role).filter(Role.id == rol_id).delete()

    db.commit()

    return {"message": f"El rol con id {rol_id} y todos los usuarios relacionados han sido eliminados"}
