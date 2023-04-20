from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    contrasena = Column(String, nullable=False)

    firmas = relationship("Firma", back_populates="usuario")
    tokens_sesion = relationship("TokenSesion", back_populates="usuario")


class Firma(Base):
    __tablename__ = "firmas"

    id = Column(Integer, primary_key=True, index=True)
    archivo_p12 = Column(LargeBinary, nullable=False)
    contrasena_p12 = Column(LargeBinary, nullable=False)
    token_p12 = Column(String, nullable=False, unique=True)
    clave_cifrado = Column(String, nullable=False, unique=True)

    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    usuario = relationship("Usuario", back_populates="firmas")

    archivos_firmados = relationship("ArchivoFirmado", back_populates="firma")


class TokenSesion(Base):
    __tablename__ = "tokens_sesion"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, nullable=False, unique=True)
    fecha_expiracion = Column(DateTime, nullable=False)

    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    usuario = relationship("Usuario", back_populates="tokens_sesion")


class ArchivoFirmado(Base):
    __tablename__ = "archivosfirmados"

    id = Column(Integer, primary_key=True, index=True)
    nombre_archivo = Column(String, nullable=False)
    fecha_hora_firma = Column(DateTime, nullable=False)
    archivo_firmado = Column(LargeBinary, nullable=False)

    firma_id = Column(Integer, ForeignKey("firmas.id"))
    firma = relationship("Firma", back_populates="archivos_firmados")

    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    usuario = relationship("Usuario")
