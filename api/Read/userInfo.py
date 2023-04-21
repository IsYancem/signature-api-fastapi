from fastapi import APIRouter, Depends
from models import UsuarioInfo
from services import get_user_by_username, get_role_name_by_id
from dependencies import get_current_user

userInfo_router = APIRouter()

@userInfo_router.get("/user-info", response_model=UsuarioInfo)
async def get_user_info(current_user: dict = Depends(get_current_user)):
    user = get_user_by_username(current_user["username"])
    role_name = get_role_name_by_id(user[5])
    user_info = UsuarioInfo(
        username=user[1],
        correo=user[3],
        nombre_rol=role_name
    )
    return user_info
