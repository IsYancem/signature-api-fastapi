import secrets
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from dependencies import get_current_user
from models import Firma
from services import get_firma_by_id, update_firma_nombre, get_api_token_by_name_and_user_id, update_api_token_by_name_and_user_id

updateFirmas_route = APIRouter()

@updateFirmas_route.put("/updateSignature/{firma_id}", status_code=status.HTTP_200_OK)
async def update_signature(
    firma_id: int,
    nombre: str = Form(None),
    current_user: dict = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado, no existe el usuario activo")

    firma = get_firma_by_id(firma_id)
    if not firma:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Firma no encontrada")

    if firma.usuario_id != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado, no puede actualizar esta firma")

    if not nombre:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El campo nombre es requerido")

    update_firma_nombre(firma_id, nombre)

    return {"message": "Nombre de firma actualizado exitosamente"}


# Conseguir Token actual de la firma
@updateFirmas_route.get("/get_api_token/{name}")
async def get_api_token(name: str, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado, no existe el usuario activo")

    user_id = current_user["id"]
    api_token = get_api_token_by_name_and_user_id(name, user_id)

    if api_token is None:
        raise HTTPException(status_code=404, detail="No se encontró el token para el nombre de la firma y el usuario actual")

    return {"api_token": api_token[0]}


# Actualizar el Token de una Firma
@updateFirmas_route.put("/update_api_token/{name}")
async def update_api_token(name: str, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado, no existe el usuario activo")

    user_id = current_user["id"]
    api_key = secrets.token_hex(32)
    updated_rows, new_api_key = update_api_token_by_name_and_user_id(name, api_key, user_id)

    if updated_rows == 0:
        raise HTTPException(status_code=404, detail="No se encontró el token para el nombre de la firma y el usuario actual")

    return {"message": "Token actualizado exitosamente", "new_api_key": new_api_key}