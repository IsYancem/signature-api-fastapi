from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from dependencies import get_current_user
from models import Firma
from services import get_firma_by_id, update_firma_nombre

updateSignature_route = APIRouter()

@updateSignature_route.put("/updateSignature/{firma_id}", status_code=status.HTTP_200_OK)
async def update_signature(
    firma_id: int,
    nombre: str = Form(None),
    current_user: dict = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado, no existe el usuario activo")

    firma = get_firma_by_id(firma_id)
    if not firma:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Firma no encontrada")

    if firma.usuario_id != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado, no puede actualizar esta firma")

    if not nombre:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El campo nombre es requerido")

    update_firma_nombre(firma_id, nombre)

    return {"message": "Nombre de firma actualizado exitosamente"}
