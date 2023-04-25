from fastapi import APIRouter, Depends, Header, HTTPException
from datetime import datetime
from typing import List, Optional
from dependencies import get_current_user
from database import SessionLocal
from models import ArchivoFirmado, Firma, TokenSesion, SignedFile

signed_by_user_route = APIRouter()

@signed_by_user_route.get("/signed", response_model=List[SignedFile])
async def get_signed_files(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado, no existe el usuario activo")

    user_id = current_user["id"]
    db = SessionLocal()
    
    try:
        archivosfirmados = db.query(
            ArchivoFirmado.id,
            ArchivoFirmado.nombre_archivo,
            ArchivoFirmado.fecha_hora_firma,
            Firma.nombre.label("nombre_firma")
        ).join(
            Firma,
            Firma.id == ArchivoFirmado.firma_id
        ).filter(
            ArchivoFirmado.usuario_id == user_id
        ).all()

        signed_files = []
        for archivo_firmado in archivosfirmados:
            signed_files.append(SignedFile(
                id=archivo_firmado.id,
                nombre_archivo=archivo_firmado.nombre_archivo,
                fecha_hora_firma=archivo_firmado.fecha_hora_firma.strftime("%Y-%m-%d %H:%M:%S"),
                nombre_firma=archivo_firmado.nombre_firma
            ))

        return signed_files
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener archivos firmados: {str(e)}")
