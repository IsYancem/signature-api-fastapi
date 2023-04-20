from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status, Form
from pydantic import BaseModel
import secrets
import base64
from cryptography.fernet import Fernet
from models import Firma
from services import create_firma
from login import get_current_user


register_signature_route = APIRouter()

@register_signature_route.post("/register-signature", status_code=status.HTTP_201_CREATED)
async def register_signature(
    nombre: str = Form(...),
    contrasena_p12: str = Form(...),
    archivo_p12: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado, no existe el usuario activo")

    key = Fernet.generate_key()
    cipher_suite = Fernet(key)
    encrypted_password = cipher_suite.encrypt(contrasena_p12.encode("utf-8"))
    encrypted_p12_file = cipher_suite.encrypt(archivo_p12.file.read())

    api_key = secrets.token_hex(32)
    new_firma = Firma(
    nombre=nombre,
    archivo_p12=encrypted_p12_file,
    contrasena_p12=encrypted_password,
    token_p12=api_key,
    usuario_id=current_user["id"]
)
    create_firma(new_firma)

    return {"message": "Firma registrada con éxito", "API key": api_key}
