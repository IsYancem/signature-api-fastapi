from services import get_firmas_by_user_id
from dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException

showFirmas_route = APIRouter()

@showFirmas_route.get("/user-signatures")
async def get_user_signatures(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado, no existe el usuario activo")

    user_id = current_user["id"]
    firmas = get_firmas_by_user_id(user_id)

    return {"firmas": firmas}
