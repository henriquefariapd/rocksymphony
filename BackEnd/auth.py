# auth.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models import User
from schemas import UserResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Função para hashear a senha
def hash_password(password: str):
    return pwd_context.hash(password)

# Função para verificar senha
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Função para autenticar o usuário
def authenticate_user(username: str, password: str, db: Session) -> UserResponse:
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return UserResponse(username=user.username, email=user.username)  # Mudado para username no retorno
