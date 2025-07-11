import requests
import json

def test_login():
    """Testa o login com diferentes credenciais"""
    
    base_url = "http://localhost:8000"
    
    # Credenciais para testar
    credentials = [
        {"email": "leonahoum@gmail.com", "password": "admin123"},
        {"email": "admin@rocksymphony.com", "password": "admin123"},
        {"email": "leonahoum@gmail.com", "password": "admin"},
    ]
    
    for cred in credentials:
        print(f"\n🧪 Testando login com: {cred['email']}")
        
        try:
            response = requests.post(
                f"{base_url}/auth/login",
                json=cred,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Login realizado com sucesso!")
                print(f"📧 Email: {data['user']['email']}")
                print(f"👤 Usuário: {data['user'].get('usuario', 'N/A')}")
                print(f"👨‍💼 Admin: {data['user']['is_admin']}")
                print(f"🔑 Token: {data['access_token'][:50]}...")
                break
            else:
                print(f"❌ Erro {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
    
    else:
        print("\n❌ Nenhuma credencial funcionou!")
        print("💡 Soluções:")
        print("1. Resetar senha no Dashboard do Supabase")
        print("2. Criar novo usuário admin")
        print("3. Verificar se o servidor está rodando")

if __name__ == "__main__":
    print("🎸 Rock Symphony - Teste de Login")
    print("=" * 50)
    test_login()
