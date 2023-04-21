from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from services import get_user_by_username, get_user_by_email, create_or_update_session_token, get_session_token_by_user_id
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

JWT_SECRET_KEY = "jwt_secret_key"
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600 * 24  # 1 dia

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
login_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Optional[dict]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado, no existe el nombre de usuario")

        user = get_user_by_username(username)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado, no existe el usuario ")

        session_token = get_session_token_by_user_id(user[0])
        if session_token is None or session_token[1] != token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado, no existe un token de sesión válido")

        return {"id": user[0], "username": user[1], "correo": user[3], "role_id": user[5]}
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"No autorizado ={e}")

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
        'sub': user[1],
        'user_id': user[0],
        'exp': datetime.now() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    # Creamos o actualizamos el token de sesión
    create_or_update_session_token(user[0], token)

    return {'token': token}
