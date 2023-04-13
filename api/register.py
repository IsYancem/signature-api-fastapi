from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import create_user, get_user_by_username, get_user_by_email
from passlib.context import CryptContext

register_router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    username: str
    password: str
    email: str

@register_router.post("/register")
async def register(user: UserCreate):
    existing_user_username = get_user_by_username(user.username)
    if existing_user_username:
        raise HTTPException(status_code=400, detail="Nombre de usuario ya registrado")
    
    existing_user_email = get_user_by_email(user.email)
    if existing_user_email:
        raise HTTPException(status_code=400, detail="Correo electrónico ya registrado")
    
    if not user.username or not user.password or not user.email:
        raise HTTPException(status_code=400, detail="Por favor complete todos los campos")
    
    if len(user.username) < 4 or len(user.username) > 20:
        raise HTTPException(status_code=400, detail="El nombre de usuario debe tener entre 4 y 20 caracteres")
    
    if len(user.password) < 8 or len(user.password) > 50:
        raise HTTPException(status_code=400, detail="La contraseña debe tener entre 8 y 50 caracteres")
    
    if pwd_context.identify(user.password) is not None:
        raise HTTPException(status_code=400, detail="La contraseña no es lo suficientemente segura")
    
    if "@" not in user.email or "." not in user.email:
        raise HTTPException(status_code=400, detail="El correo electrónico no es válido")
    
    create_user(user.username, pwd_context.hash(user.password), user.email)
    return {"status": "ok", "message": "Usuario creado exitosamente"}
