#!/usr/bin/env python3
"""
Script para adicionar a coluna tracking_code na tabela orders do Supabase
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def add_tracking_code_column():
    """Adiciona a coluna tracking_code na tabela orders"""
    
    # Configurar cliente Supabase
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ Erro: SUPABASE_URL e SUPABASE_ANON_KEY devem estar definidas no .env")
        return False
    
    try:
        supabase: Client = create_client(url, key)
        
        # SQL para adicionar a coluna
        sql_query = """
        ALTER TABLE orders 
        ADD COLUMN IF NOT EXISTS tracking_code VARCHAR(255);
        """
        
        print("🔄 Adicionando coluna tracking_code na tabela orders...")
        
        # Executar a query usando rpc (se disponível) ou diretamente
        try:
            # Tentar executar diretamente
            result = supabase.rpc('exec_sql', {'sql': sql_query}).execute()
            print("✅ Coluna tracking_code adicionada com sucesso!")
            return True
            
        except Exception as e:
            print(f"⚠️  Não foi possível executar via RPC: {e}")
            print("📝 Execute manualmente no Supabase SQL Editor:")
            print("   ALTER TABLE orders ADD COLUMN IF NOT EXISTS tracking_code VARCHAR(255);")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao conectar com Supabase: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando adição da coluna tracking_code...")
    success = add_tracking_code_column()
    
    if success:
        print("✅ Processo concluído com sucesso!")
    else:
        print("⚠️  Execute o SQL manualmente no Supabase:")
        print("   ALTER TABLE orders ADD COLUMN IF NOT EXISTS tracking_code VARCHAR(255);")
