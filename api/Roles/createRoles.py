from fastapi import APIRouter, Depends, HTTPException, status, Form
from typing import List, Optional
from sqlalchemy.orm import Session
from database import get_db
from models import Role
from schemas import RoleCreate
from dependencies import get_current_user

createRoles_route = APIRouter()

@createRoles_route.post("/roles", status_code=status.HTTP_201_CREATED)
async def create_role(
    role: RoleCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user or current_user["role_id"] != 1:
        raise HTTPException(status_code=401, detail="No autorizado")

    db_role = Role(
        nombre=role.nombre,
        max_archivos=role.max_archivos,
        max_firmas=role.max_firmas
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)

    return {"message": "Rol creado exitosamente", "id": db_role.id}
