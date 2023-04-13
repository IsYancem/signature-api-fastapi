from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from login import  JWT_SECRET_KEY, JWT_ALGORITHM
import jwt
from jwt import PyJWTError


def is_token_valid(token: str):
    try:
        jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return True
    except PyJWTError:
        return False

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if not is_token_valid(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return token

auth_router = APIRouter()

# Ahora puedes agregar la dependencia `verify_token` a las rutas que quieras proteger:
@auth_router.get("/protected-route", dependencies=[Depends(verify_token)])
async def protected_route():
    return {"message": "Esta ruta está protegida"}