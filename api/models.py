from pydantic import BaseModel
from typing import Optional
from fastapi import Form, Body

# Modelo de Roles
class Role(BaseModel):
    id: Optional[int]
    nombre: str

# Modelo de Usuarios
class Usuario(BaseModel):
    id: Optional[int]
    username: str
    password: str
    correo: str
    estado: bool
    role_id: int

# Modelo de TokensSesion
class TokenSesion(BaseModel):
    id: Optional[int]
    token: str
    fecha_expiracion: str
    usuario_id: int

# Modelo de Firmas
class Firma(BaseModel):
    id: Optional[int]
    nombre: str
    archivo_p12: bytes
    contrasena_p12: bytes
    token_p12: str
    clave_cifrado: str
    usuario_id: int

# Modelo de ArchivosFirmados
class ArchivoFirmado(BaseModel):
    id: Optional[int]
    nombre_archivo: str
    fecha_hora_firma: str
    firma_id: int
    usuario_id: int

#Esto estoy utilizando xd
class UpdatePassword(BaseModel):
    new_password: str
    new_password_confirmation: str 

class UserCreate(BaseModel):
    username: str
    password: str
    correo: str
    role_id: int

