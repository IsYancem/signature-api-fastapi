from services import update_user_password
from dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from models import UpdatePassword
import bcrypt

updateUserPassword_route = APIRouter()

@updateUserPassword_route.post("/update_user_password")
async def update_user_password_api(password: UpdatePassword, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado, no existe el usuario activo")
    
    if password.new_password != password.new_password_confirmation:
        raise HTTPException(status_code=400, detail="Las contraseñas no coinciden")
    
    # Cifrar la nueva contraseña
    hashed_password = bcrypt.hashpw(password.new_password.encode("utf-8"), bcrypt.gensalt())

    user_id = current_user["id"]
    update_user_password(user_id, hashed_password.decode("utf-8"))
    return {"message": "Contraseña actualizada exitosamente"}