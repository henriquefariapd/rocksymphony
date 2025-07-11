from fastapi import APIRouter, Depends, HTTPException
from schemas_auth import UserRegister, UserLogin, UserResponse, TokenResponse, PasswordReset
from auth_supabase import auth_service, get_current_user, get_current_admin_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=dict)
async def register(user_data: UserRegister):
    """Registrar novo usuário"""
    return await auth_service.register_user(
        email=user_data.email,
        usuario=user_data.usuario,
        password=user_data.password,
        is_admin=user_data.is_admin
    )

@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    """Fazer login com email e senha"""
    return await auth_service.login_user(
        email=user_data.email,
        password=user_data.password
    )

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Fazer logout"""
    return await auth_service.logout_user()

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Obter dados do usuário atual"""
    return current_user

@router.post("/reset-password")
async def reset_password(reset_data: PasswordReset):
    """Solicitar reset de senha"""
    return await auth_service.reset_password(reset_data.email)

@router.get("/admin-only")
async def admin_only(current_user: dict = Depends(get_current_admin_user)):
    """Endpoint apenas para administradores"""
    return {"message": "Acesso liberado para admin", "user": current_user}
