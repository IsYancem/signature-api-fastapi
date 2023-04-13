from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from database import get_user_by_username, get_user_by_email, update_user_token

JWT_SECRET_KEY = "jwt_secret_key"
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600  # 1 hora

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
login_router = APIRouter()


@login_router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not form_data.username or not form_data.password:
        raise HTTPException(status_code=400, detail="Debe ingresar un nombre de usuario y una contraseña")
    if "@" in form_data.username:
        user = get_user_by_email(form_data.username)
    else:
        user = get_user_by_username(form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Nombre de usuario o correo electrónico incorrecto")
    if not pwd_context.verify(form_data.password, user[2]):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")
    if user[3] == 0:
        raise HTTPException(status_code=403, detail="Cuenta desactivada")
    if user[4] == 0:
        raise HTTPException(status_code=403, detail="Usuario bloqueado")
    token = jwt.encode({
        'user_id': user[0],
        'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    update_user_token(user[1], token)

    return {'token': token}
