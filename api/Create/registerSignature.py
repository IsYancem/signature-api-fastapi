from datetime import datetime
import os
import secrets
import shutil
import base64

from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from OpenSSL import crypto
from typing import Tuple
from cryptography.fernet import Fernet

from models import Firma, Usuario, Role
from dependencies import get_current_user 
from services import create_firma
from database import get_db


register_signature_route = APIRouter()


@register_signature_route.post("/register-signature", status_code=status.HTTP_201_CREATED)
async def register_signature(
    nombre: str = Form(None),
    contrasena_p12: str = Form(None),
    archivo_p12: UploadFile = File(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
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

    # Verificar límite de firmas por usuario
    max_firmas = (
        db.query(Role.max_firmas)
        .join(Usuario, Usuario.role_id == Role.id)
        .filter(Usuario.id == current_user["id"])
        .scalar()
    )
    
    if max_firmas is not None:
        firmas_actuales = (
            db.query(Firma)
            .filter(Firma.usuario_id == current_user["id"])
            .count()
        )
        
        if firmas_actuales >= max_firmas:
            raise HTTPException(status_code=400, detail=f"El usuario ha alcanzado el límite máximo de {max_firmas} firmas")

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

