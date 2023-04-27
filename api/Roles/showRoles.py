from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models import Role
from dependencies import get_current_user
from database import get_db


showRoles_route = APIRouter()

@showRoles_route.get("/roles", status_code=status.HTTP_200_OK)
async def get_roles(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user or current_user["role_id"] != 1:
        raise HTTPException(status_code=401, detail="No autorizado")

    roles = db.query(Role).all()
    return roles
