#!/usr/bin/env python3
"""
Script simples para verificar conexão com banco
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Carregar variáveis de ambiente
load_dotenv()

def check_connection():
    """Verificar conexão simples com o banco"""
    try:
        # Configurar conexão
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL não encontrada no .env")
            return False
        
        print(f"🔗 Conectando ao banco: {database_url[:20]}...")
        
        # Criar engine
        engine = create_engine(database_url, echo=False)
        
        # Testar conexão simples
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            if result.fetchone():
                print("✅ Conexão OK")
                
                # Verificar se schema public existe
                result = conn.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'public'"))
                if result.fetchone():
                    print("✅ Schema public existe")
                else:
                    print("❌ Schema public não existe")
                
                # Listar algumas tabelas
                result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' LIMIT 5"))
                tables = result.fetchall()
                print(f"📋 Primeiras 5 tabelas: {[row[0] for row in tables]}")
                
                return True
        
    except Exception as e:
        print(f"❌ Erro na conexão: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Verificando conexão com banco...")
    if check_connection():
        print("✅ Verificação concluída com sucesso")
    else:
        print("❌ Falha na verificação")
