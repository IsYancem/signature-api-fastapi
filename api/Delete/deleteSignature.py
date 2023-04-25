from services import delete_firma_by_id
from dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException

deleteSignature_route = APIRouter()

@deleteSignature_route.delete("/delete-signature/{signature_id}")
async def delete_signature(signature_id: int, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado, no existe el usuario activo")

    user_id = current_user["id"]
    deleted_rows = delete_firma_by_id(signature_id, user_id)

    if deleted_rows == 0:
        raise HTTPException(status_code=404, detail="No se encontró la firma a eliminar")

    return {"message": "Firma eliminada exitosamente"}