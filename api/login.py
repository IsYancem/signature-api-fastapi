from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from database import get_user_by_username, update_user_token

JWT_SECRET_KEY = "jwt_secret_key"
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600  # 1 hora

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
login_router = APIRouter()


@login_router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_username(form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Usuario y/o contraseña incorrectos")
    if not pwd_context.verify(form_data.password, user[2]):
        raise HTTPException(status_code=400, detail="Usuario y/o contraseña incorrectos")
    token = jwt.encode({
        'user_id': user[0],
        'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    

    update_user_token(user[1], token)

    return {'token': token}
