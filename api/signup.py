from fastapi import APIRouter, HTTPException, status
from models import UserCreate
import bcrypt
from models import Usuario
from services import create_user, get_user_by_email_or_username

register_route = APIRouter()

@register_route.post("/signup", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    existing_user = get_user_by_email_or_username(user.correo, user.username)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo o nombre de usuario ya están en uso",
        )

    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())

    new_user = Usuario(
        username=user.username,
        password=hashed_password.decode("utf-8"),
        correo=user.correo,
        estado=True,
        role_id=user.role_id
    )
    create_user(new_user)

    return {"message": "Usuario registrado con éxito"}
