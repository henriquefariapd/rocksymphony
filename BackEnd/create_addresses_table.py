#!/usr/bin/env python3
"""
Script para criar a tabela de endereços no Supabase
Execute: python create_addresses_table.py
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def create_addresses_table():
    """Cria a tabela de endereços no Supabase"""
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL não encontrada no arquivo .env")
        print("Certifique-se de que o arquivo .env existe e contém a DATABASE_URL do Supabase")
        return False
    
    try:
        # Conectar ao banco
        engine = create_engine(DATABASE_URL)
        
        # Ler o arquivo SQL
        sql_file_path = os.path.join(os.path.dirname(__file__), 'create_addresses_table.sql')
        
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Executar o SQL
        with engine.connect() as connection:
            # Dividir o SQL em comandos individuais
            sql_commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
            
            for command in sql_commands:
                if command:
                    print(f"Executando: {command[:50]}...")
                    connection.execute(text(command))
            
            connection.commit()
        
        print("✅ Tabela 'addresses' criada com sucesso!")
        print("✅ Políticas RLS configuradas!")
        print("✅ Índices criados!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Criando tabela de endereços...")
    
    success = create_addresses_table()
    
    if success:
        print("\n🎉 Configuração concluída!")
        print("Agora você pode usar os endpoints de endereços na API.")
    else:
        print("\n💥 Falha na criação da tabela.")
        sys.exit(1)
