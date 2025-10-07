import os
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

# Configuração do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
#SUPABASE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar definidos no .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Bearer token dependency
security = HTTPBearer()

# Importações com fallback para local e Heroku
try:
    from .models import User
    from .supabase_client import supabase as supabase_client
except ImportError:
    from models import User
    from supabase_client import supabase as supabase_client

class AuthService:
    def __init__(self):
        self.supabase = supabase

    async def register_user(self, email: str, usuario: str, password: str, is_admin: bool = False):
        """Registra um novo usuário"""
        try:
            # Verificar se o usuario já existe
            import pdb; pdb.set_trace()
            if usuario:
                existing_user = self.supabase.table("users").select("*").eq("usuario", usuario).execute()
                if existing_user.data:
                    raise HTTPException(
                        status_code=400,
                        detail="Usuário já existe"
                    )
            
            # Criar usuário no Supabase Auth
            auth_response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "data": {
                    "usuario": usuario,
                    "is_admin": is_admin
                }
            })
            
            if auth_response.user:
                # Criar entrada na tabela users incluindo o email
                user_data = {
                    "id": auth_response.user.id,
                    "usuario": usuario,
                    "email": email,  # Salvar email na nossa tabela
                    "is_admin": is_admin
                }
                
                self.supabase.table("users").insert(user_data).execute()
                
                return {
                    "user": auth_response.user,
                    "message": "Usuário criado com sucesso! Verifique seu email."
                }
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Erro ao criar usuário"
                )
                
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Erro ao registrar usuário: {str(e)}"
            )

    async def login_user(self, email: str, password: str):
        """Faz login do usuário com email e senha"""
        try:
            print(f"[DEBUG] Tentando fazer login para: {email}")
            
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user and auth_response.session:
                print(f"[DEBUG] Login bem-sucedido para usuário: {auth_response.user.id}")
                
                # Buscar dados completos do usuário
                try:
                    user_data = self.supabase.table("users").select("*").eq("id", auth_response.user.id).execute()
                    print(f"[DEBUG] Resultado da busca na tabela users no login: {user_data}")
                    
                    user_info = {
                        "id": auth_response.user.id,
                        "email": auth_response.user.email,
                        "usuario": user_data.data[0].get("usuario") if user_data.data and len(user_data.data) > 0 else None,
                        "is_admin": user_data.data[0].get("is_admin", False) if user_data.data and len(user_data.data) > 0 else False
                    }
                    
                    print(f"[DEBUG] Dados do usuário: {user_info}")
                    
                    return {
                        "access_token": auth_response.session.access_token,
                        "token_type": "bearer",
                        "user": user_info,
                        "expires_in": auth_response.session.expires_in
                    }
                except Exception as query_error:
                    print(f"[DEBUG] Erro ao buscar usuário na tabela users no login: {str(query_error)}")
                    # Retornar dados básicos mesmo se não conseguir buscar na tabela users
                    user_info = {
                        "id": auth_response.user.id,
                        "email": auth_response.user.email,
                        "usuario": None,
                        "is_admin": False
                    }
                    
                    return {
                        "access_token": auth_response.session.access_token,
                        "token_type": "bearer",
                        "user": user_info,
                        "expires_in": auth_response.session.expires_in
                    }
            else:
                print(f"[DEBUG] Login falhou - resposta inválida")
                raise HTTPException(
                    status_code=401,
                    detail="Email ou senha incorretos"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            print(f"[DEBUG] Erro ao fazer login: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail=f"Erro ao fazer login: {str(e)}"
            )

    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Obtém o usuário atual pelo token"""
        try:
            token = credentials.credentials
            print(f"[DEBUG] Validando token: {token[:20]}...")
            
            # Verificar token no Supabase
            user_response = self.supabase.auth.get_user(token)
            
            if user_response.user:
                print(f"[DEBUG] Usuário encontrado no Supabase Auth: {user_response.user.id}")
                
                # Buscar dados adicionais na tabela users
                try:
                    user_data = self.supabase.table("users").select("*").eq("id", user_response.user.id).execute()
                    print(f"[DEBUG] Resultado da busca na tabela users: {user_data}")
                    
                    if user_data.data and len(user_data.data) > 0:
                        print(f"[DEBUG] Dados encontrados na tabela users: {user_data.data[0]}")
                        return {
                            "id": user_response.user.id,
                            "email": user_response.user.email,
                            "usuario": user_data.data[0].get("usuario"),
                            "is_admin": user_data.data[0].get("is_admin", False),
                            "created_at": user_data.data[0].get("created_at")
                        }
                    else:
                        print(f"[DEBUG] Nenhum dado encontrado na tabela users para o ID: {user_response.user.id}")
                        print(f"[DEBUG] user_data.data: {user_data.data}")
                        # Retornar dados básicos do Supabase Auth
                        return {
                            "id": user_response.user.id,
                            "email": user_response.user.email,
                            "usuario": None,
                            "is_admin": False
                        }
                except Exception as query_error:
                    print(f"[DEBUG] Erro ao buscar usuário na tabela users: {str(query_error)}")
                    # Retornar dados básicos do Supabase Auth
                    return {
                        "id": user_response.user.id,
                        "email": user_response.user.email,
                        "usuario": None,
                        "is_admin": False
                    }
            else:
                print(f"[DEBUG] Token inválido - user_response.user é None")
                raise HTTPException(
                    status_code=401,
                    detail="Token inválido"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            print(f"[DEBUG] Erro ao validar token: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail=f"Erro ao validar token: {str(e)}"
            )

    async def logout_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Faz logout do usuário"""
        try:
            token = credentials.credentials
            self.supabase.auth.sign_out()
            return {"message": "Logout realizado com sucesso"}
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Erro ao fazer logout: {str(e)}"
            )

    async def reset_password(self, email: str):
        """Envia email para reset de senha"""
        try:
            # Configurar a URL de redirecionamento para nossa página de reset
            # Detectar se estamos em desenvolvimento ou produção
            import os
            if os.getenv("ENVIRONMENT") == "production":
                redirect_url = "https://rocksymphony-3f7b8e8b3afd.herokuapp.com/reset-password"
            else:
                redirect_url = "http://localhost:5173/reset-password"
            
            # Usar o método correto do Supabase
            response = self.supabase.auth.reset_password_email(
                email,
                {
                    "redirect_to": redirect_url,
                    "data": {
                        "redirect_url": redirect_url
                    }
                }
            )
            
            print(f"[DEBUG] Reset password response: {response}")
            return {"message": "Email de recuperação enviado. Verifique sua caixa de entrada."}
        except Exception as e:
            print(f"[ERROR] Reset password error: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Erro ao enviar email de recuperação: {str(e)}"
            )

    async def update_password(self, access_token: str, refresh_token: str, new_password: str):
        """Atualiza a senha do usuário usando tokens de reset"""
        try:
            if not access_token:
                raise HTTPException(
                    status_code=400,
                    detail="Token de acesso é obrigatório"
                )
            
            print(f"[DEBUG] Updating password with token: {access_token[:20]}...")
            
            # Definir a sessão com os tokens
            session_response = self.supabase.auth.set_session(access_token, refresh_token)
            
            if not session_response.user:
                raise HTTPException(
                    status_code=400,
                    detail="Tokens inválidos ou expirados"
                )
            
            print(f"[DEBUG] Session set successfully for user: {session_response.user.id}")
            
            # Atualizar a senha
            update_response = self.supabase.auth.update_user({
                "password": new_password
            })
            
            if update_response.user:
                print(f"[DEBUG] Password updated successfully for user: {update_response.user.id}")
                return {"message": "Senha atualizada com sucesso"}
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Erro ao atualizar senha"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            print(f"[ERROR] Update password error: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Erro ao atualizar senha: {str(e)}"
            )
# Instância do serviço de autenticação
auth_service = AuthService()

# Dependency para obter usuário atual
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return await auth_service.get_current_user(credentials)

# Dependency para verificar se usuário é admin
async def get_current_admin_user(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=403,
            detail="Acesso negado. Apenas administradores podem acessar este recurso."
        )
    return current_user

# Dependency opcional para usuário (pode ser None)
async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))):
    if credentials:
        return await auth_service.get_current_user(credentials)
    return None
