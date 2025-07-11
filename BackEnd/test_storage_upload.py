"""
Script para testar upload no Supabase Storage
"""

try:
    from supabase_client import supabase
except ImportError:
    from BackEnd.supabase_client import supabase

def test_storage_upload():
    """Testar upload de arquivo no Storage"""
    try:
        # Criar um arquivo de teste
        test_content = b"Teste de upload"
        test_filename = "test_image.txt"
        
        print(f"[DEBUG] Testando upload para bucket 'product-images'...")
        
        # Tentar fazer upload
        storage_response = supabase.storage.from_("product-images").upload(
            test_filename, 
            test_content,
            file_options={"content-type": "text/plain"}
        )
        
        print(f"[DEBUG] Upload response: {storage_response}")
        
        if storage_response:
            print("[SUCCESS] Upload realizado com sucesso!")
            
            # Obter URL pública
            public_url = supabase.storage.from_("product-images").get_public_url(test_filename)
            print(f"[DEBUG] URL pública: {public_url}")
            
            # Listar arquivos no bucket
            files = supabase.storage.from_("product-images").list()
            print(f"[DEBUG] Arquivos no bucket: {[f['name'] for f in files]}")
            
            # Remover arquivo de teste
            delete_response = supabase.storage.from_("product-images").remove([test_filename])
            print(f"[DEBUG] Arquivo de teste removido: {delete_response}")
            
        else:
            print("[ERROR] Upload falhou!")
            
    except Exception as e:
        print(f"[ERRO] Erro ao testar upload: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_storage_upload()
