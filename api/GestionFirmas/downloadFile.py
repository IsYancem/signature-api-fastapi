from fastapi import APIRouter, Depends, Header, HTTPException, Response
from datetime import datetime
from typing import List, Optional
from dependencies import get_current_user
from database import SessionLocal
from models import ArchivoFirmado, Firma, TokenSesion, SignedFile
import io

download_file_route = APIRouter()

@download_file_route.get("/downloadFile/{id}")
async def download_file(id: int, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado, no existe el usuario activo")

    user_id = current_user["id"]
    db = SessionLocal()
    
    try:
        archivo_firmado = db.query(
            ArchivoFirmado.nombre_archivo,
            ArchivoFirmado.archivo_firmado
        ).filter(
            ArchivoFirmado.usuario_id == user_id,
            ArchivoFirmado.id == id
        ).first()

        if not archivo_firmado:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")

        nombre_archivo = archivo_firmado.nombre_archivo
        archivo_firmado_bytes = archivo_firmado.archivo_firmado

        return Response(content=archivo_firmado_bytes, media_type='application/octet-stream', headers={"Content-Disposition": f"attachment; filename={nombre_archivo}"})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener archivo firmado: {str(e)}")
