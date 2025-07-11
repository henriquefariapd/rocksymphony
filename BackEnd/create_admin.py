import os
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Configuração do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ SUPABASE_URL e SUPABASE_KEY devem estar definidos no .env")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def create_admin_user():
    """Cria o usuário admin no Supabase"""
    
    admin_email = "admin@rocksymphony.com"
    admin_password = "admin123"
    admin_usuario = "admin"
    
    try:
        print("🔐 Criando usuário admin...")
        
        # Tentar criar usuário no Supabase Auth
        try:
            auth_response = supabase.auth.sign_up({
                "email": admin_email,
                "password": admin_password,
                "options": {
                    "data": {
                        "usuario": admin_usuario,
                        "is_admin": True
                    }
                }
            })
            
            if auth_response.user:
                user_id = auth_response.user.id
                print(f"✅ Usuário criado no Supabase Auth: {user_id}")
                
                # Criar entrada na tabela users (sem email)
                user_data = {
                    "id": user_id,
                    "usuario": admin_usuario,
                    "is_admin": True
                }
                
                supabase.table("users").insert(user_data).execute()
                print("✅ Entrada criada na tabela users")
                
                print("🎉 Usuário admin criado com sucesso!")
                print(f"📧 Email: {admin_email}")
                print(f"🔑 Senha: {admin_password}")
                print(f"👤 Usuário: {admin_usuario}")
                print(f"👨‍💼 Admin: Sim")
                
                return True
                
        except Exception as signup_error:
            error_msg = str(signup_error)
            
            if "User already registered" in error_msg:
                print("⚠️  Usuário já existe! Tentando fazer login...")
                
                # Fazer login para obter o ID do usuário
                login_response = supabase.auth.sign_in_with_password({
                    "email": admin_email,
                    "password": admin_password
                })
                
                if login_response.user:
                    user_id = login_response.user.id
                    print(f"✅ Login realizado: {user_id}")
                    
                    # Verificar se já existe na tabela users
                    existing_user = supabase.table("users").select("*").eq("id", user_id).execute()
                    
                    if existing_user.data:
                        print("📝 Atualizando usuário existente...")
                        supabase.table("users").update({
                            "usuario": admin_usuario,
                            "is_admin": True
                        }).eq("id", user_id).execute()
                    else:
                        print("📝 Criando entrada na tabela users...")
                        user_data = {
                            "id": user_id,
                            "usuario": admin_usuario,
                            "is_admin": True
                        }
                        supabase.table("users").insert(user_data).execute()
                    
                    print("✅ Usuário admin configurado com sucesso!")
                    print(f"📧 Email: {admin_email}")
                    print(f"🔑 Senha: {admin_password}")
                    print(f"👤 Usuário: {admin_usuario}")
                    print(f"👨‍💼 Admin: Sim")
                    
                    return True
                else:
                    print("❌ Erro ao fazer login. Verifique a senha.")
                    return False
            else:
                print(f"❌ Erro ao criar usuário: {error_msg}")
                return False
                
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

def test_login():
    """Testa o login do usuário admin"""
    
    print("\n🧪 Testando login do admin...")
    
    try:
        login_response = supabase.auth.sign_in_with_password({
            "email": "admin@rocksymphony.com",
            "password": "admin123"
        })
        
        if login_response.user:
            print("✅ Login realizado com sucesso!")
            print(f"👤 ID: {login_response.user.id}")
            print(f"📧 Email: {login_response.user.email}")
            
            # Buscar dados na tabela users
            user_data = supabase.table("users").select("*").eq("id", login_response.user.id).execute()
            
            if user_data.data:
                user_info = user_data.data[0]
                print(f"👤 Usuário: {user_info.get('usuario')}")
                print(f"👨‍💼 Admin: {user_info.get('is_admin')}")
            
            return True
        else:
            print("❌ Falha no login")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de login: {e}")
        return False

if __name__ == "__main__":
    print("🎸 Rock Symphony - Script de Criação do Usuário Admin")
    print("=" * 60)
    
    success = create_admin_user()
    
    if success:
        test_login()
        print("\n✅ Processo concluído com sucesso!")
        print("🚀 Agora você pode fazer login com:")
        print("   Email: admin@rocksymphony.com")
        print("   Senha: admin123")
    else:
        print("\n❌ Falha na criação do usuário admin")
        print("💡 Tente criar manualmente via Dashboard do Supabase")
