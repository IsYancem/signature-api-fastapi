from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary, BLOB, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from fastapi import Form, Body

# from models import ArchivoFirmado, Firma, TokenSesion, Usuario, Role

Base = declarative_base()

class SignedFile:
    def __init__(
        self, 
        nombre_archivo: str, 
        fecha_hora_firma: datetime, 
        nombre_firma: str
    ):
        self.nombre_archivo = nombre_archivo
        self.fecha_hora_firma = fecha_hora_firma
        self.nombre_firma = nombre_firma


class ArchivoFirmado(Base):
    __tablename__ = "ArchivosFirmados"

    id = Column(Integer, primary_key=True, index=True)
    nombre_archivo = Column(String(255), nullable=False)
    fecha_hora_firma = Column(DateTime, nullable=False)
    firma_id = Column(Integer, ForeignKey("Firmas.id"))
    usuario_id = Column(Integer, ForeignKey("Usuarios.id"))
    archivo_firmado = Column(BLOB, nullable=False)

class Firma(Base):
    __tablename__ = "Firmas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    archivo_p12 = Column(BLOB, nullable=False)
    contrasena_p12 = Column(BLOB, nullable=False)
    token_p12 = Column(String(255), nullable=False)
    clave_cifrado = Column(Text, nullable=False)
    usuario_id = Column(Integer, ForeignKey("Usuarios.id"))
    fecha_caducidad = Column(DateTime, nullable=False)

class TokenSesion(Base):
    __tablename__ = "TokensSesion"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), nullable=False)
    fecha_expiracion = Column(DateTime, nullable=False)
    usuario_id = Column(Integer, ForeignKey("Usuarios.id"))

class Usuario(Base):
    __tablename__ = "Usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    estado = Column(Boolean, nullable=False)
    role_id = Column(Integer, ForeignKey("Roles.id"))

class Role(Base):
    __tablename__ = "Roles"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)

class UserCreate(BaseModel):
    username: str
    password: str
    correo: str
    role_id: int

# Obtener Informacion sobre el usuario
class UsuarioInfo(BaseModel):
    username: str
    correo: str
    nombre_rol: str

# Obtener Informacion sobre firmas de un usuario
class SignedFile(BaseModel):
    id: Optional[int]
    nombre_archivo: str
    fecha_hora_firma: str
    nombre_firma: str

#Esto estoy utilizando xd
class UpdatePassword(BaseModel):
    new_password: str
    new_password_confirmation: str 