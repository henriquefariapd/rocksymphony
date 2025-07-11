#!/usr/bin/env python3
"""
Script para verificar produtos no banco de dados
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import Product, SessionLocal
from supabase_client import supabase

def check_local_products():
    """Verificar produtos no banco local (SQLite)"""
    print("=== VERIFICANDO PRODUTOS NO BANCO LOCAL (SQLite) ===")
    
    try:
        db = SessionLocal()
        products = db.query(Product).all()
        
        print(f"Total de produtos encontrados: {len(products)}")
        
        if products:
            for product in products:
                print(f"ID: {product.id}, Nome: {product.name}, Artista: {product.artist}, Valor: R$ {product.valor}")
        else:
            print("Nenhum produto encontrado no banco local")
            
        db.close()
        
    except Exception as e:
        print(f"Erro ao verificar produtos locais: {str(e)}")

def check_supabase_products():
    """Verificar produtos no Supabase"""
    print("\n=== VERIFICANDO PRODUTOS NO SUPABASE ===")
    
    try:
        response = supabase.table("products").select("*").execute()
        
        print(f"Total de produtos encontrados no Supabase: {len(response.data)}")
        
        if response.data:
            for product in response.data:
                print(f"ID: {product.get('id')}, Nome: {product.get('name')}, Artista: {product.get('artist')}, Valor: R$ {product.get('valor')}")
        else:
            print("Nenhum produto encontrado no Supabase")
            
    except Exception as e:
        print(f"Erro ao verificar produtos no Supabase: {str(e)}")

def main():
    print("VERIFICANDO PRODUTOS NOS BANCOS DE DADOS\n")
    
    check_local_products()
    check_supabase_products()

if __name__ == "__main__":
    main()
