from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_current_user
from database import get_db
from models import Role

updateRoles_route = APIRouter()

@updateRoles_route.put("/roles/{rol_id}", status_code=status.HTTP_200_OK)
async def update_rol(
    rol_id: int,
    nombre: Optional[str] = Form(None),
    max_archivos: Optional[int] = Form(None),
    max_firmas: Optional[int] = Form(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user or current_user["role_id"] != 1:
        raise HTTPException(status_code=401, detail="No autorizado")

    rol = db.query(Role).filter(Role.id == rol_id).first()
    if not rol:
        raise HTTPException(status_code=404, detail="El rol no existe")

    if nombre is not None:
        rol.nombre = nombre

    if max_archivos is not None:
        rol.max_archivos = max_archivos

    if max_firmas is not None:
        rol.max_firmas = max_firmas

    db.commit()

    return {"message": f"El rol con id {rol_id} ha sido actualizado"}