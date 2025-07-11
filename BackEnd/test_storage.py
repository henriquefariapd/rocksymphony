"""
Script para testar e configurar o Supabase Storage
"""

try:
    from supabase_client import supabase
except ImportError:
    from BackEnd.supabase_client import supabase

def test_storage():
    """Testar conexão com o Supabase Storage"""
    try:
        # Listar buckets
        buckets = supabase.storage.list_buckets()
        print(f"[DEBUG] Buckets disponíveis: {buckets}")
        
        # Verificar se o bucket product-images existe
        bucket_names = [bucket.name for bucket in buckets]
        
        if "product-images" not in bucket_names:
            print("[DEBUG] Bucket 'product-images' não encontrado.")
            print("[DEBUG] Você precisa criar o bucket manualmente no Supabase:")
            print("1. Acesse o painel do Supabase")
            print("2. Vá em Storage")
            print("3. Crie um novo bucket chamado 'product-images'")
            print("4. Marque como 'Public bucket'")
            return
        else:
            print("[DEBUG] Bucket 'product-images' existe!")
            
        # Listar arquivos no bucket
        files = supabase.storage.from_("product-images").list()
        print(f"[DEBUG] Arquivos no bucket: {files}")
        
        # Testar URL pública de um arquivo se existir
        if files:
            first_file = files[0]
            public_url = supabase.storage.from_("product-images").get_public_url(first_file['name'])
            print(f"[DEBUG] URL pública do primeiro arquivo: {public_url}")
            
    except Exception as e:
        print(f"[ERRO] Erro ao testar storage: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_storage()
