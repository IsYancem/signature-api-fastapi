from datetime import datetime
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status, Form
from pydantic import BaseModel
import secrets
import base64
from cryptography.fernet import Fernet
from models import Firma
from services import create_firma
from login import get_current_user
from typing import Tuple
import os
from OpenSSL import crypto

register_signature_route = APIRouter()

@register_signature_route.post("/register-signature", status_code=status.HTTP_201_CREATED)
async def register_signature(
    nombre: str = Form(None),
    contrasena_p12: str = Form(None),
    archivo_p12: UploadFile = File(None),
    current_user: dict = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado, no existe el usuario activo")

    if not nombre:
        raise HTTPException(status_code=400, detail="El campo nombre es requerido")

    if not contrasena_p12:
        raise HTTPException(status_code=400, detail="La contraseña del archivo P12 es requerida")

    if not archivo_p12:
        raise HTTPException(status_code=400, detail="El archivo P12 es requerido")

    # Validar que el archivo p12 sea válido
    archivo_p12_content = archivo_p12.file.read()
    try:
        p12 = crypto.load_pkcs12(archivo_p12_content, contrasena_p12)
    except Exception:
        raise HTTPException(status_code=400, detail="El archivo P12 no es válido o la contraseña no es correcta")

    # Verificar que el certificado no haya caducado
    cert = p12.get_certificate()
    cert_expiry_date = cert.get_notAfter().decode('utf-8')
    cert_expiry_date = datetime.strptime(cert_expiry_date, "%Y%m%d%H%M%SZ")
    if cert_expiry_date < datetime.utcnow():
        raise HTTPException(status_code=400, detail="El certificado ha caducado")

    # Calcular el tiempo que falta para que caduque el certificado
    time_to_expire = cert_expiry_date - datetime.utcnow()

    # Agregar un campo a la base de datos para almacenar la llave de cifrado
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)
    encrypted_password = cipher_suite.encrypt(contrasena_p12.encode("utf-8"))
    encrypted_p12_file = cipher_suite.encrypt(archivo_p12_content)
    clave_cifrado = key.decode()

    # Guardar la fecha de caducidad en la base de datos
    fecha_caducidad = cert_expiry_date.strftime("%Y-%m-%d %H:%M:%S")

    api_key = secrets.token_hex(32)
    new_firma = Firma(
        nombre=nombre,
        archivo_p12=encrypted_p12_file,
        contrasena_p12=encrypted_password,
        token_p12=api_key,
        usuario_id=current_user["id"],
        clave_cifrado=clave_cifrado,
        fecha_caducidad=fecha_caducidad
    )
    create_firma(new_firma)

    return {
        "message": "Firma registrada con éxito",
        "API key": api_key,
        "tiempo_restante": f"{time_to_expire.days} días, {time_to_expire.seconds//3600} horas y {(time_to_expire.seconds//60)%60} minutos para la caducidad",
        "fecha_caducidad": cert_expiry_date.strftime("%Y-%m-%d %H:%M:%S")
    }
