from datetime import date
import json
import csv
import random
import string
from sqlite3 import OperationalError
from urllib.parse import urlparse, parse_qs
from fastapi import FastAPI, Depends, HTTPException, Request, Security, UploadFile, File, status, Form
from sqlalchemy import Date, text
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
import os
from fpdf import FPDF
import tempfile
import requests

import mercadopago
import yagmail

# Importações para desenvolvimento local
from models import Order, OrderProduct, SessionLocal, Product, ShoppingCart, ShoppingCartProduct, User

# Importações do sistema de autenticação Supabase
from auth_routes import router as auth_router
from auth_supabase import get_current_user, get_current_admin_user, get_current_user_optional
from supabase_client import supabase

# Criação da instância do FastAPI
app = FastAPI(title="Rock Symphony API", version="1.0.0", description="Marketplace de CDs de Rock")

# Configuração do MercadoPago
mp = mercadopago.SDK("APP_USR-6446237437103604-040119-bca68443def1fb05bfa6643f416e2192-96235831")

# Configuração de arquivos estáticos
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ],  # URLs do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas de autenticação
app.include_router(auth_router)

# Função para obter a sessão do banco de dados
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função para converter o usuário do Supabase para o formato esperado pelo sistema
def get_user_from_supabase(current_user: dict, db: Session):
    """Converte o usuário do Supabase para o formato esperado pelos endpoints"""
    user = db.query(User).filter(User.id == current_user["id"]).first()
    
    if not user:
        # Se não encontrar, criar um novo usuário com os dados do Supabase
        user = User(
            id=current_user["id"],
            usuario=current_user.get("usuario", ""),
            is_admin=current_user.get("is_admin", False)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user

# Endpoints básicos da API
@app.get("/")
async def root():
    return {"message": "Rock Symphony API - Marketplace de CDs de Rock", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Rock Symphony API"}

@app.get("/health_db")
def health_db():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "ok"}
    except OperationalError:
        return {"status": "error", "message": "Database connection failed"}, 500

# ===== ENDPOINTS DE PRODUTOS =====

@app.get("/api/products")
async def get_available_products(current_user: dict = Depends(get_current_user)):
    """Buscar todos os produtos disponíveis"""
    print(f"[DEBUG] Buscando produtos para usuário: {current_user['id']}")
    
    try:
        # Buscar produtos no Supabase
        response = supabase.table("products").select("*").execute()
        
        print(f"[DEBUG] Produtos encontrados no Supabase: {len(response.data) if response.data else 0}")
        
        if response.data:
            print(f"[DEBUG] Primeiro produto: {response.data[0]}")
            return response.data
        else:
            print("[DEBUG] Nenhum produto encontrado no Supabase")
            raise HTTPException(status_code=404, detail="Produtos não encontrados")
            
    except Exception as e:
        print(f"[DEBUG] Erro ao buscar produtos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar produtos: {str(e)}")

class ProductCreate(BaseModel):
    name: str
    artist: str
    description: str
    valor: float
    remaining: int

@app.post("/api/products")
async def create_new_product(
    name: str = Form(...),
    artist: str = Form(...),
    description: str = Form(...),
    valor: float = Form(...),
    remaining: int = Form(...),
    file: UploadFile = File(None),
    current_user: dict = Depends(get_current_user)  # Mudei para get_current_user temporariamente
):
    """Criar um novo produto (apenas admin)"""
    try:
        print(f"[DEBUG] Criando produto: {name} - {artist}")
        print(f"[DEBUG] Usuário: {current_user['id']} (admin: {current_user.get('is_admin')})")
        
        # Verificar se é admin
        if not current_user.get('is_admin'):
            print(f"[DEBUG] Usuário não é admin: {current_user}")
            raise HTTPException(status_code=403, detail="Apenas administradores podem criar produtos")
        
        image_path = None
        if file and file.filename:
            print(f"[DEBUG] Processando arquivo: {file.filename}")
            
            # Tentar salvar no Supabase Storage primeiro
            try:
                # Ler o conteúdo do arquivo
                file_content = await file.read()
                file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
                file_name = f"{name.replace(' ', '_')}_{int(datetime.now().timestamp())}.{file_extension}"
                
                # Upload para o Supabase Storage
                storage_response = supabase.storage.from_("product-images").upload(
                    file_name, 
                    file_content,
                    file_options={"content-type": f"image/{file_extension}"}
                )
                
                print(f"[DEBUG] Upload response: {storage_response}")
                
                if storage_response:
                    # Obter a URL pública da imagem
                    public_url = supabase.storage.from_("product-images").get_public_url(file_name)
                    image_path = public_url
                    print(f"[DEBUG] Imagem salva no Supabase Storage: {image_path}")
                
            except Exception as storage_error:
                print(f"[DEBUG] Erro ao fazer upload para Supabase Storage: {str(storage_error)}")
                print(f"[DEBUG] Tentando salvar localmente...")
                
                # Fallback: salvar localmente
                try:
                    # Resetar o arquivo para o início
                    await file.seek(0)
                    file_content = await file.read()
                    
                    file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
                    file_name = f"{name.replace(' ', '_')}_{int(datetime.now().timestamp())}.{file_extension}"
                    file_path = os.path.join("uploads", file_name)
                    
                    with open(file_path, "wb") as buffer:
                        buffer.write(file_content)
                    
                    image_path = f"uploads/{file_name}"
                    print(f"[DEBUG] Imagem salva localmente: {image_path}")
                    
                except Exception as local_error:
                    print(f"[DEBUG] Erro ao salvar localmente: {str(local_error)}")
                    image_path = None
        
        # Criar novo produto no Supabase
        new_product = {
            "name": name,
            "artist": artist,
            "description": description,
            "valor": float(valor),
            "remaining": remaining,
            "image_path": image_path
        }
        
        print(f"[DEBUG] Dados do produto: {new_product}")
        
        response = supabase.table("products").insert(new_product).execute()
        
        print(f"[DEBUG] Resposta do Supabase: {response}")
        
        if response.data:
            print(f"[DEBUG] Produto criado com sucesso: {response.data[0]}")
            return {"message": f"Produto '{name}' criado com sucesso!", "product": response.data[0]}
        else:
            print(f"[DEBUG] Erro: response.data está vazio")
            raise HTTPException(status_code=500, detail="Erro ao criar produto no banco")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[DEBUG] Erro ao criar produto: {str(e)}")
        print(f"[DEBUG] Tipo do erro: {type(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar produto: {str(e)}")

class ProductUpdate(BaseModel):
    name: str
    artist: str
    description: str
    valor: float
    remaining: int

@app.put("/api/products/{product_id}")
async def edit_product(
    product_id: int, 
    product: ProductUpdate, 
    current_user: dict = Depends(get_current_admin_user)
):
    """Editar um produto existente (apenas admin)"""
    try:
        # Atualizar produto no Supabase
        response = supabase.table("products").update({
            "name": product.name,
            "artist": product.artist,
            "description": product.description,
            "valor": product.valor,
            "remaining": product.remaining
        }).eq("id", product_id).execute()
        
        if response.data:
            return {"message": f"Produto '{product.name}' atualizado com sucesso!"}
        else:
            raise HTTPException(status_code=404, detail="Produto não encontrado")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao editar produto: {str(e)}")

@app.delete("/api/products/{product_id}")
async def delete_product(
    product_id: int, 
    current_user: dict = Depends(get_current_user)  # Mudei para get_current_user
):
    """Excluir um produto (apenas admin)"""
    try:
        print(f"[DEBUG] Deletando produto ID: {product_id}")
        print(f"[DEBUG] Usuário: {current_user['id']} (admin: {current_user.get('is_admin')})")
        
        # Verificar se é admin
        if not current_user.get('is_admin'):
            print(f"[DEBUG] Usuário não é admin")
            raise HTTPException(status_code=403, detail="Apenas administradores podem deletar produtos")
        
        # Buscar produto antes de deletar para obter o nome e imagem
        product_response = supabase.table("products").select("*").eq("id", product_id).execute()
        
        if not product_response.data:
            print(f"[DEBUG] Produto não encontrado")
            raise HTTPException(status_code=404, detail="Produto não encontrado")
        
        product = product_response.data[0]
        product_name = product["name"]
        image_path = product.get("image_path")
        
        print(f"[DEBUG] Produto encontrado: {product_name}")
        print(f"[DEBUG] Imagem: {image_path}")
        
        # Deletar produto do Supabase
        response = supabase.table("products").delete().eq("id", product_id).execute()
        
        print(f"[DEBUG] Resposta da deleção: {response}")
        
        # Tentar deletar a imagem se existir
        if image_path:
            try:
                if image_path.startswith("uploads/"):
                    # Imagem local
                    import os
                    local_path = os.path.join("uploads", image_path.split("/")[-1])
                    if os.path.exists(local_path):
                        os.remove(local_path)
                        print(f"[DEBUG] Imagem local deletada: {local_path}")
                else:
                    # Imagem no Supabase Storage
                    file_name = image_path.split("/")[-1]
                    storage_response = supabase.storage.from_("product-images").remove([file_name])
                    print(f"[DEBUG] Imagem do Supabase Storage deletada: {storage_response}")
                    
            except Exception as img_error:
                print(f"[DEBUG] Erro ao deletar imagem: {str(img_error)}")
                # Não falhar se não conseguir deletar a imagem
        
        return {"message": f"Produto '{product_name}' excluído com sucesso!"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[DEBUG] Erro ao deletar produto: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao excluir produto: {str(e)}")

# ===== ENDPOINTS DE CARRINHO =====

class AddProductToCartRequest(BaseModel):
    productId: int
    quantity: int = 1

@app.post("/api/add_product_to_cart")
def add_product_to_cart(
    newProduct: AddProductToCartRequest, 
    db: Session = Depends(get_db_session), 
    current_user: dict = Depends(get_current_user)
):
    """Adicionar produto ao carrinho"""
    user = get_user_from_supabase(current_user, db)
    
    # Encontrar ou criar carrinho do usuário
    shopping_cart = db.query(ShoppingCart).filter(ShoppingCart.user_id == user.id).first()
    
    if not shopping_cart:
        shopping_cart = ShoppingCart(user_id=user.id)
        db.add(shopping_cart)
        db.commit()
        db.refresh(shopping_cart)
    
    # Verificar se o produto já está no carrinho
    cart_product = db.query(ShoppingCartProduct).filter(
        ShoppingCartProduct.shoppingcart_id == shopping_cart.id,
        ShoppingCartProduct.product_id == newProduct.productId
    ).first()
    
    if cart_product:
        # Atualizar quantidade
        cart_product.quantity += newProduct.quantity
    else:
        # Adicionar novo produto
        cart_product = ShoppingCartProduct(
            shoppingcart_id=shopping_cart.id,
            product_id=newProduct.productId,
            quantity=newProduct.quantity
        )
        db.add(cart_product)
    
    db.commit()
    db.refresh(cart_product)
    return {"message": "Produto adicionado ao carrinho", "cart_product": cart_product}

@app.get("/api/get_cart_products")
def get_cart_products(
    db: Session = Depends(get_db_session), 
    current_user: dict = Depends(get_current_user)
):
    """Obter produtos do carrinho"""
    user = get_user_from_supabase(current_user, db)
    shopping_cart = db.query(ShoppingCart).filter(ShoppingCart.user_id == user.id).first()

    if not shopping_cart:
        return []

    # Buscar os produtos do carrinho
    cart_items = db.query(ShoppingCartProduct, Product).join(Product).filter(
        ShoppingCartProduct.shoppingcart_id == shopping_cart.id
    ).all()

    result = []
    for cart_item, product in cart_items:
        result.append({
            "id": product.id,
            "name": product.name,
            "artist": product.artist,
            "valor": product.valor,
            "quantity": cart_item.quantity,
            "image_path": product.image_path
        })

    return result

# ===== ENDPOINTS DE PEDIDOS =====

@app.post("/api/handle_checkout")
def create_order(
    db: Session = Depends(get_db_session), 
    current_user: dict = Depends(get_current_user)
):
    """Criar pedido a partir do carrinho"""
    user = get_user_from_supabase(current_user, db)
    shopping_cart = db.query(ShoppingCart).filter(ShoppingCart.user_id == user.id).first()

    if not shopping_cart:
        raise HTTPException(status_code=404, detail="Carrinho não encontrado")

    # Obter os produtos do carrinho
    cart_products = db.query(ShoppingCartProduct).filter(
        ShoppingCartProduct.shoppingcart_id == shopping_cart.id
    ).all()

    if not cart_products:
        raise HTTPException(status_code=400, detail="Carrinho está vazio")

    # Criar o pedido
    new_order = Order(
        order_date=date.today(),
        user_id=user.id,
        payment_link=None,
        pending=True,
        active=True
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # Adicionar produtos ao pedido
    total_value = 0
    for cart_product in cart_products:
        product = db.query(Product).filter(Product.id == cart_product.product_id).first()
        
        order_product = OrderProduct(
            order_id=new_order.id,
            product_id=cart_product.product_id,
            quantity=cart_product.quantity
        )
        db.add(order_product)
        
        total_value += product.valor * cart_product.quantity

    # Limpar carrinho
    for cart_product in cart_products:
        db.delete(cart_product)

    db.commit()
    
    return {
        "message": "Pedido criado com sucesso",
        "order_id": new_order.id,
        "total_value": total_value
    }

@app.get("/api/orders")
async def get_user_orders(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Obter pedidos do usuário"""
    user = get_user_from_supabase(current_user, db)
    orders = db.query(Order).filter(Order.user_id == user.id).all()
    
    result = []
    for order in orders:
        order_products = db.query(OrderProduct, Product).join(Product).filter(
            OrderProduct.order_id == order.id
        ).all()
        
        products = []
        total_value = 0
        for order_product, product in order_products:
            products.append({
                "name": product.name,
                "artist": product.artist,
                "quantity": order_product.quantity,
                "valor": product.valor
            })
            total_value += product.valor * order_product.quantity
        
        result.append({
            "id": order.id,
            "order_date": order.order_date.isoformat(),
            "pending": order.pending,
            "active": order.active,
            "products": products,
            "total_value": total_value
        })
    
    return result

# ===== ENDPOINTS DE ADMINISTRAÇÃO =====

@app.get("/api/admin/users")
async def list_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db_session), 
    current_user: dict = Depends(get_current_admin_user)
):
    """Listar usuários (apenas admin)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@app.get("/api/admin/orders")
async def get_all_orders(
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db_session)
):
    """Obter todos os pedidos (apenas admin)"""
    orders = db.query(Order).all()
    
    result = []
    for order in orders:
        user = db.query(User).filter(User.id == order.user_id).first()
        order_products = db.query(OrderProduct, Product).join(Product).filter(
            OrderProduct.order_id == order.id
        ).all()
        
        products = []
        total_value = 0
        for order_product, product in order_products:
            products.append({
                "name": product.name,
                "artist": product.artist,
                "quantity": order_product.quantity,
                "valor": product.valor
            })
            total_value += product.valor * order_product.quantity
        
        result.append({
            "id": order.id,
            "order_date": order.order_date.isoformat(),
            "pending": order.pending,
            "active": order.active,
            "user": {
                "id": user.id,
                "usuario": user.usuario,
                "email": current_user.get("email")  # Email vem do Supabase
            },
            "products": products,
            "total_value": total_value
        })
    
    return result

# ===== ENDPOINTS DE USUÁRIO =====

@app.get("/api/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Obter informações do usuário atual"""
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "usuario": current_user.get("usuario"),
        "is_admin": current_user.get("is_admin", False)
    }

# ===== ENDPOINT TEMPORÁRIO PARA DEBUG =====

@app.get("/api/debug/user")
async def debug_user(current_user: dict = Depends(get_current_user)):
    """Debug: verificar dados do usuário atual"""
    try:
        print(f"[DEBUG] Verificando usuário: {current_user['id']}")
        
        # Tentar buscar diretamente no Supabase
        user_response = supabase.table("users").select("*").eq("id", current_user['id']).execute()
        print(f"[DEBUG] Resposta da busca: {user_response}")
        
        return {
            "current_user": current_user,
            "supabase_query": user_response.data,
            "found_in_table": len(user_response.data) > 0,
            "is_admin": user_response.data[0].get("is_admin") if user_response.data else False
        }
    except Exception as e:
        print(f"[DEBUG] Erro no debug: {str(e)}")
        return {"error": str(e), "current_user": current_user}

# ===== FIM DO DEBUG =====

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
