#!/usr/bin/env python3
"""
Script para testar criação de produto sem imagem
"""

import requests
import json

# Configurações
API_URL = "http://127.0.0.1:8000"
TOKEN = "YOUR_TOKEN_HERE"  # Substitua pelo seu token

def create_product_without_image():
    """Criar produto sem imagem para teste"""
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
    }
    
    # Dados do produto
    data = {
        "name": "Appetite for Destruction",
        "artist": "Guns N' Roses",
        "description": "Álbum de estreia da banda Guns N' Roses",
        "valor": 29.99,
        "remaining": 10
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/products",
            headers=headers,
            data=data
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
    except Exception as e:
        print(f"Erro: {str(e)}")

if __name__ == "__main__":
    print("Para usar este script:")
    print("1. Faça login no frontend")
    print("2. Copie o token do localStorage")
    print("3. Substitua 'YOUR_TOKEN_HERE' pelo token real")
    print("4. Execute o script")
