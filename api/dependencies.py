from typing import Optional
from fastapi import HTTPException, Depends, status
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta
from config import SECRET_KEY, ALGORITHM

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import jwt
from services import get_user_by_username, get_user_by_email, create_or_update_session_token, get_session_token_by_user_id

JWT_SECRET_KEY = "jwt_secret_key"
JWT_ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class TokenData(BaseModel):
    id: Optional[int] = None

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