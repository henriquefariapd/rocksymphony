from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    email: EmailStr
    usuario: str  # Campo usuario (display name)
    password: str
    is_admin: bool = False

class UserLogin(BaseModel):
    email: EmailStr  # Login por email
    password: str

class UserResponse(BaseModel):
    id: str
    email: str  # Vem do Supabase Auth
    usuario: Optional[str] = None
    is_admin: bool
    created_at: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: dict

class PasswordReset(BaseModel):
    email: EmailStr
