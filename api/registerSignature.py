from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status, Form
from pydantic import BaseModel
import secrets
import base64
from cryptography.fernet import Fernet
from models import Firma
from services import create_firma
from login import get_current_user
from typing import Tuple

class SignatureCreate(BaseModel):
    nombre: str
    archivo_p12: UploadFile
    contrasena_p12: str
    usuario_id: str

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

    # Agregamos un campo a la base de datos para almacenar la llave de cifrado
    clave_cifrado = key.decode()

    api_key = secrets.token_hex(32)
    new_firma = Firma(
        nombre=nombre,
        archivo_p12=encrypted_p12_file,
        contrasena_p12=encrypted_password,
        token_p12=api_key,
        usuario_id=current_user["id"],
        clave_cifrado=clave_cifrado  # Guardamos la clave de cifrado en la base de datos
    )
    create_firma(new_firma)

    return {"message": "Firma registrada con éxito", "API key": api_key}

