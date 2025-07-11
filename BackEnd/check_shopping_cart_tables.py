#!/usr/bin/env python3
"""
Script para verificar e criar tabelas de carrinho no banco de dados
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do banco
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL não encontrada no .env")
    sys.exit(1)

print(f"🔗 Conectando ao banco: {DATABASE_URL[:20]}...")

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        print("✅ Conexão estabelecida com sucesso")
        
        # Verificar se as tabelas existem
        print("\n📋 Verificando tabelas existentes...")
        
        # Consultar tabelas
        result = session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('shoppingcarts', 'shoppingcart_products')
            ORDER BY table_name;
        """))
        
        existing_tables = [row[0] for row in result.fetchall()]
        print(f"Tabelas de carrinho encontradas: {existing_tables}")
        
        # Verificar tabelas necessárias
        required_tables = ['shoppingcarts', 'shoppingcart_products']
        missing_tables = [table for table in required_tables if table not in existing_tables]
        
        if missing_tables:
            print(f"❌ Tabelas faltando: {missing_tables}")
            print("📝 Execute o script setup_shopping_cart_tables.sql no Supabase SQL Editor")
        else:
            print("✅ Todas as tabelas de carrinho estão presentes")
            
            # Testar inserção básica
            print("\n🧪 Testando estrutura das tabelas...")
            
            # Contar registros
            try:
                result = session.execute(text("SELECT COUNT(*) FROM public.shoppingcarts"))
                carts_count = result.scalar()
                print(f"📊 Carrinhos existentes: {carts_count}")
                
                result = session.execute(text("SELECT COUNT(*) FROM public.shoppingcart_products"))
                cart_products_count = result.scalar()
                print(f"📊 Produtos em carrinhos: {cart_products_count}")
                
                print("✅ Estrutura das tabelas está funcionando")
                
            except Exception as e:
                print(f"❌ Erro ao acessar tabelas: {e}")
                print("🔧 Verifique as permissões e políticas RLS")
        
        # Verificar se existe algum usuário para teste
        print("\n👥 Verificando usuários...")
        try:
            result = session.execute(text("SELECT COUNT(*) FROM public.users"))
            users_count = result.scalar()
            print(f"📊 Usuários cadastrados: {users_count}")
            
            if users_count > 0:
                result = session.execute(text("SELECT id, usuario FROM public.users LIMIT 1"))
                user = result.fetchone()
                if user:
                    print(f"👤 Usuário de teste: {user[1]} (ID: {user[0]})")
            
        except Exception as e:
            print(f"❌ Erro ao verificar usuários: {e}")
        
        # Verificar produtos
        print("\n🛍️ Verificando produtos...")
        try:
            result = session.execute(text("SELECT COUNT(*) FROM public.products"))
            products_count = result.scalar()
            print(f"📊 Produtos cadastrados: {products_count}")
            
            if products_count > 0:
                result = session.execute(text("SELECT id, name FROM public.products LIMIT 1"))
                product = result.fetchone()
                if product:
                    print(f"🎵 Produto de teste: {product[1]} (ID: {product[0]})")
            
        except Exception as e:
            print(f"❌ Erro ao verificar produtos: {e}")

except Exception as e:
    print(f"❌ Erro na conexão: {e}")
    sys.exit(1)

print("\n🎉 Verificação concluída!")
