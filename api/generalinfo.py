from services import *
from login import get_current_user
from fastapi import APIRouter, Depends, HTTPException, Form
import secrets
from models import UpdatePassword
import bcrypt

info_signature_route = APIRouter()

@info_signature_route.get("/user-signatures")
async def get_user_signatures(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado, no existe el usuario activo")

    user_id = current_user["id"]
    firmas = get_firmas_by_user_id(user_id)

    return {"firmas": firmas}


@info_signature_route.delete("/delete-signature/{signature_id}")
async def delete_signature(signature_id: int, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado, no existe el usuario activo")

    user_id = current_user["id"]
    deleted_rows = delete_firma_by_id(signature_id, user_id)

    if deleted_rows == 0:
        raise HTTPException(status_code=404, detail="No se encontró la firma a eliminar")

    return {"message": "Firma eliminada exitosamente"}

@info_signature_route.post("/update_user_password")
async def update_user_password_api(password: UpdatePassword, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado, no existe el usuario activo")
    
    if password.new_password != password.new_password_confirmation:
        raise HTTPException(status_code=400, detail="Las contraseñas no coinciden")
    
    # Cifrar la nueva contraseña
    hashed_password = bcrypt.hashpw(password.new_password.encode("utf-8"), bcrypt.gensalt())


    user_id = current_user["id"]
    update_user_password(user_id, hashed_password.decode("utf-8"))
    return {"message": "Contraseña actualizada exitosamente"}


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
