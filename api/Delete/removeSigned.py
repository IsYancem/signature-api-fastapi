from fastapi import APIRouter, Depends, HTTPException, Body
from dependencies import get_current_user
from database import SessionLocal
from models import ArchivoFirmado, TokenSesion
from typing import List

remove_signed_route = APIRouter()

@remove_signed_route.delete("/removeSigned")
async def remove_signed_files(ids_archivos: List[int] = Body(...), current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado, no existe el usuario activo")

    user_id = current_user["id"]
    db = SessionLocal()
    
    try:
        for id_archivo in ids_archivos:
            archivo_firmado = db.query(ArchivoFirmado).filter(ArchivoFirmado.id == id_archivo, ArchivoFirmado.usuario_id == user_id).first()
            if not archivo_firmado:
                raise HTTPException(status_code=404, detail=f"Archivo con id {id_archivo} no encontrado o no pertenece al usuario")
            db.delete(archivo_firmado)
        db.commit()
        return {"message": "Archivos eliminados exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar archivos: {str(e)}")
