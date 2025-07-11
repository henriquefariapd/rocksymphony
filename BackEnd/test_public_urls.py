"""
Script para testar URLs públicas do Supabase Storage
"""

try:
    from supabase_client import supabase
except ImportError:
    from BackEnd.supabase_client import supabase

def test_public_urls():
    """Testar URLs públicas das imagens no bucket"""
    try:
        # Listar arquivos no bucket
        files = supabase.storage.from_("product-images").list()
        print(f"[DEBUG] Arquivos no bucket: {len(files)}")
        
        for file in files[:3]:  # Mostrar apenas os primeiros 3
            file_name = file['name']
            print(f"\n[DEBUG] Arquivo: {file_name}")
            
            # Obter URL pública
            public_url = supabase.storage.from_("product-images").get_public_url(file_name)
            print(f"[DEBUG] URL pública: {public_url}")
            
            # Testar se a URL está acessível
            import requests
            try:
                response = requests.head(public_url, timeout=10)
                print(f"[DEBUG] Status da URL: {response.status_code}")
                print(f"[DEBUG] Headers: {dict(response.headers)}")
                if response.status_code == 200:
                    print("✅ URL acessível")
                else:
                    print(f"❌ URL não acessível: {response.status_code}")
            except Exception as req_error:
                print(f"❌ Erro ao testar URL: {str(req_error)}")
            
    except Exception as e:
        print(f"[ERRO] Erro ao testar URLs: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_public_urls()
