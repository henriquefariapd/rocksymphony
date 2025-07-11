import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Configuração do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_user_uuid():
    """Busca o UUID do usuário admin"""
    
    admin_email = "admin@rocksymphony.com"
    
    try:
        # Fazer login para obter o UUID
        login_response = supabase.auth.sign_in_with_password({
            "email": admin_email,
            "password": "admin123"
        })
        
        if login_response.user:
            user_id = login_response.user.id
            
            print("✅ UUID encontrado!")
            print(f"📧 Email: {admin_email}")
            print(f"🆔 UUID: {user_id}")
            print(f"📅 Criado em: {login_response.user.created_at}")
            
            print("\n📋 SQL para inserir na tabela users:")
            print(f"""
INSERT INTO users (id, usuario, is_admin, created_at) 
VALUES (
    '{user_id}', 
    'admin',
    TRUE,
    NOW()
) 
ON CONFLICT (id) 
DO UPDATE SET 
    usuario = 'admin',
    is_admin = TRUE;
            """)
            
            # Tentar inserir automaticamente
            try:
                user_data = {
                    "id": user_id,
                    "usuario": "admin",
                    "is_admin": True
                }
                
                # Verificar se já existe
                existing = supabase.table("users").select("*").eq("id", user_id).execute()
                
                if existing.data:
                    print("⚠️  Usuário já existe na tabela users, atualizando...")
                    supabase.table("users").update({
                        "usuario": "admin",
                        "is_admin": True
                    }).eq("id", user_id).execute()
                    print("✅ Usuário atualizado com sucesso!")
                else:
                    print("📝 Inserindo usuário na tabela users...")
                    supabase.table("users").insert(user_data).execute()
                    print("✅ Usuário inserido com sucesso!")
                    
            except Exception as insert_error:
                print(f"⚠️  Erro ao inserir automaticamente: {insert_error}")
                print("💡 Execute o SQL manualmente no Dashboard do Supabase")
            
            return user_id
            
        else:
            print("❌ Usuário não encontrado ou senha incorreta")
            print("💡 Verifique se o usuário foi criado no Supabase Dashboard")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao buscar UUID: {e}")
        print("💡 Certifique-se que o usuário admin foi criado no Supabase")
        return None

def create_user_in_table(user_id):
    """Cria o usuário na tabela users"""
    
    try:
        user_data = {
            "id": user_id,
            "usuario": "admin",
            "is_admin": True
        }
        
        result = supabase.table("users").insert(user_data).execute()
        
        if result.data:
            print("✅ Usuário criado na tabela users!")
            return True
        else:
            print("❌ Erro ao criar usuário na tabela")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    print("🎸 Rock Symphony - Buscar UUID do Admin")
    print("=" * 50)
    
    # Primeiro, tentar buscar o UUID
    uuid = get_user_uuid()
    
    if uuid:
        print(f"\n🎉 Processo concluído!")
        print(f"🆔 UUID do admin: {uuid}")
        print("✅ Agora você pode usar este UUID nas consultas SQL")
    else:
        print("\n❌ Não foi possível encontrar o UUID")
        print("📝 Passos para resolver:")
        print("1. Vá no Supabase Dashboard")
        print("2. Authentication > Users")
        print("3. Clique em 'Add user'")
        print("4. Email: admin@rocksymphony.com")
        print("5. Password: admin123")
        print("6. Execute este script novamente")
