from services import get_api_token_by_name_and_user_id, update_api_token_by_name_and_user_id
from dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException
import secrets

info_signature_route = APIRouter()

@info_signature_route.get("/get_api_token/{name}")
async def get_api_token(name: str, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado, no existe el usuario activo")

    user_id = current_user["id"]
    api_token = get_api_token_by_name_and_user_id(name, user_id)

    if api_token is None:
        raise HTTPException(status_code=404, detail="No se encontró el token para el nombre de la firma y el usuario actual")

    return {"api_token": api_token[0]}

@info_signature_route.put("/update_api_token/{name}")
async def update_api_token(name: str, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado, no existe el usuario activo")

    user_id = current_user["id"]
    api_key = secrets.token_hex(32)
    updated_rows, new_api_key = update_api_token_by_name_and_user_id(name, api_key, user_id)

    if updated_rows == 0:
        raise HTTPException(status_code=404, detail="No se encontró el token para el nombre de la firma y el usuario actual")

    return {"message": "Token actualizado exitosamente", "new_api_key": new_api_key}