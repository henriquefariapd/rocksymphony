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

# Importações para desenvolvimento local e Heroku
try:
    # Tentativa para Heroku (import relativo)
    from .models import Order, OrderProduct, SessionLocal, Product, ShoppingCart, ShoppingCartProduct, User
except ImportError:
    # Fallback para desenvolvimento local (import absoluto)
    from models import Order, OrderProduct, SessionLocal, Product, ShoppingCart, ShoppingCartProduct, User

# Importações do sistema de autenticação Supabase
try:
    # Tentativa para desenvolvimento local (import absoluto)
    from auth_routes import router as auth_router
    from auth_supabase import get_current_user, get_current_admin_user, get_current_user_optional
    from supabase_client import supabase
except ImportError:
    try:
        # Tentativa para Heroku (import relativo)
        from .auth_routes import router as auth_router
        from .auth_supabase import get_current_user, get_current_admin_user, get_current_user_optional
        from .supabase_client import supabase
    except ImportError:
        # Fallback final
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from auth_routes import router as auth_router
        from auth_supabase import get_current_user, get_current_admin_user, get_current_user_optional
        from supabase_client import supabase

def get_supabase_client():
    """Função helper para obter cliente Supabase (funciona local e Heroku)"""
    return supabase

# Criação da instância do FastAPI
app = FastAPI(title="Rock Symphony API", version="1.0.0", description="Marketplace de CDs de Rock")

# Configuração do MercadoPago
mp = mercadopago.SDK("APP_USR-6446237437103604-040119-bca68443def1fb05bfa6643f416e2192-96235831")

# Configuração de arquivos estáticos
# Assets do frontend (CSS, JS do Vite)
frontend_assets_path = Path(os.getcwd()) / "FrontEnd" / "dist" / "assets"
if frontend_assets_path.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_assets_path)), name="assets")

# Configuração para servir o frontend React (se existir)
frontend_dist_path = Path(os.getcwd()) / "FrontEnd" / "dist"
if frontend_dist_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dist_path)), name="static")

# NOTA: Imagens de produtos são servidas diretamente do Supabase Storage
# Não precisamos mais servir uploads locais

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "https://rocksymphony-3f7b8e8b3afd.herokuapp.com",
        "http://rocksymphony-3f7b8e8b3afd.herokuapp.com"
    ],  # URLs do frontend (local e produção)
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
    try:
        print(f"=== DEBUG GET_USER_FROM_SUPABASE ===")
        print(f"Buscando usuário com ID: {current_user['id']}")
        print(f"Tipo do ID: {type(current_user['id'])}")
        
        # Tentar query simples primeiro
        print("Executando query...")
        user = db.query(User).filter(User.id == current_user["id"]).first()
        print(f"Query executada. Usuário encontrado: {user}")
        
        if not user:
            print("Usuário não encontrado, criando novo...")
            # Se não encontrar, criar um novo usuário com os dados do Supabase
            user_data = {
                "id": current_user["id"],
                "usuario": current_user.get("usuario", ""),
                "is_admin": current_user.get("is_admin", False)
            }
            print(f"Dados para criar usuário: {user_data}")
            
            user = User(**user_data)
            print("Objeto User criado")
            
            db.add(user)
            print("User adicionado à sessão")
            
            db.commit()
            print("Commit realizado")
            
            db.refresh(user)
            print(f"Usuário criado e refreshed: {user}")
        
        print(f"Retornando usuário: {user.id}")
        return user
        
    except Exception as e:
        print(f"ERRO em get_user_from_supabase: {str(e)}")
        print(f"Tipo do erro: {type(e)}")
        import traceback
        traceback.print_exc()
        raise

# Função helper para importar supabase (compatível com local e Heroku)
def get_supabase():
    """Importa o cliente supabase (compatível com local e Heroku)"""
    return supabase

# Endpoints básicos da API
@app.get("/api/info")
async def api_info():
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
            
            # Salvar imagem no Supabase Storage
            try:
                # Ler o conteúdo do arquivo
                file_content = await file.read()
                file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
                file_name = f"{name.replace(' ', '_')}_{int(datetime.now().timestamp())}.{file_extension}"
                
                print(f"[DEBUG] Fazendo upload da imagem: {file_name}")
                
                # Upload para o Supabase Storage
                storage_response = supabase.storage.from_("product-images").upload(
                    file_name, 
                    file_content,
                    file_options={"content-type": f"image/{file_extension}"}
                )
                
                print(f"[DEBUG] Upload response: {storage_response}")
                
                # Obter a URL pública da imagem
                public_url = supabase.storage.from_("product-images").get_public_url(file_name)
                image_path = public_url
                print(f"[DEBUG] Imagem salva no Supabase Storage: {image_path}")
                
            except Exception as storage_error:
                print(f"[ERRO] Erro ao fazer upload para Supabase Storage: {str(storage_error)}")
                import traceback
                traceback.print_exc()
                raise HTTPException(status_code=500, detail=f"Erro ao fazer upload da imagem: {str(storage_error)}")
        
        else:
            # Produto sem imagem
            image_path = None
            print(f"[DEBUG] Produto criado sem imagem")
        
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
                if "supabase" in image_path:
                    # Imagem no Supabase Storage
                    file_name = image_path.split("/")[-1]
                    storage_response = supabase.storage.from_("product-images").remove([file_name])
                    print(f"[DEBUG] Imagem do Supabase Storage deletada: {storage_response}")
                else:
                    # Imagem local (legacy)
                    print(f"[DEBUG] Ignorando imagem local: {image_path}")
                    
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
    current_user: dict = Depends(get_current_user)
):
    """Adicionar produto ao carrinho"""
    try:
        print('=== DEBUG ADD_PRODUCT_TO_CART ===')
        print(f'Dados recebidos: productId={newProduct.productId}, quantity={newProduct.quantity}')
        print(f'Usuário atual: {current_user}')

        # Usar cliente Supabase diretamente para evitar problemas de RLS
        from supabase_client import supabase
        
        user_id = current_user["id"]
        print(f'User ID: {user_id}')
        
        # Buscar ou criar carrinho do usuário
        print('Buscando carrinho do usuário...')
        cart_response = supabase.table("shoppingcarts").select("*").eq("user_id", user_id).execute()
        print(f'Resposta do carrinho: {cart_response.data}')
        
        if not cart_response.data:
            print('Criando novo carrinho...')
            cart_data = {
                "user_id": user_id
            }
            cart_response = supabase.table("shoppingcarts").insert(cart_data).execute()
            print(f'Carrinho criado: {cart_response.data}')
            cart_id = cart_response.data[0]["id"]
        else:
            cart_id = cart_response.data[0]["id"]
            print(f'Carrinho encontrado: {cart_id}')
        
        # Verificar se o produto já está no carrinho
        print('Verificando se produto já está no carrinho...')
        existing_product = supabase.table("shoppingcart_products").select("*").eq("shoppingcart_id", cart_id).eq("product_id", newProduct.productId).execute()
        print(f'Produto existente: {existing_product.data}')
        
        if existing_product.data:
            # Atualizar quantidade
            print('Atualizando quantidade...')
            new_quantity = existing_product.data[0]["quantity"] + newProduct.quantity
            update_response = supabase.table("shoppingcart_products").update({
                "quantity": new_quantity
            }).eq("shoppingcart_id", cart_id).eq("product_id", newProduct.productId).execute()
            print(f'Quantidade atualizada: {update_response.data}')
            result = update_response.data[0]
        else:
            # Adicionar novo produto
            print('Adicionando novo produto...')
            product_data = {
                "shoppingcart_id": cart_id,
                "product_id": newProduct.productId,
                "quantity": newProduct.quantity
            }
            add_response = supabase.table("shoppingcart_products").insert(product_data).execute()
            print(f'Produto adicionado: {add_response.data}')
            result = add_response.data[0]
        
        print('Operação concluída com sucesso')
        return {"message": "Produto adicionado ao carrinho", "cart_product": result}
        
    except Exception as e:
        print(f'ERRO em add_product_to_cart: {str(e)}')
        print(f'Tipo do erro: {type(e)}')
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar produto ao carrinho: {str(e)}")

@app.get("/api/get_cart_products")
def get_cart_products(current_user: dict = Depends(get_current_user)):
    """Obter produtos do carrinho do usuário"""
    try:
        print('=== DEBUG GET_CART_PRODUCTS ===')
        print(f'Usuário atual: {current_user}')
        
        from supabase_client import supabase
        
        user_id = current_user["id"]
        print(f'User ID: {user_id}')
        
        # Buscar carrinho do usuário
        print('Buscando carrinho do usuário...')
        cart_response = supabase.table("shoppingcarts").select("*").eq("user_id", user_id).execute()
        print(f'Resposta do carrinho: {cart_response.data}')
        
        if not cart_response.data:
            print('Carrinho não encontrado, criando novo carrinho...')
            # Criar carrinho automaticamente para o usuário
            cart_data = {
                "user_id": user_id
            }
            cart_response = supabase.table("shoppingcarts").insert(cart_data).execute()
            print(f'Novo carrinho criado: {cart_response.data}')
            
            # Retornar lista vazia para carrinho novo
            return []
        
        cart_id = cart_response.data[0]["id"]
        print(f'Carrinho encontrado: {cart_id}')
        
        # Buscar produtos no carrinho com join
        print('Buscando produtos no carrinho...')
        cart_products = supabase.table("shoppingcart_products").select(
            "*, product:products(*)"
        ).eq("shoppingcart_id", cart_id).execute()
        
        print(f'Produtos encontrados: {len(cart_products.data)}')
        
        # Formatar resposta
        formatted_products = []
        for item in cart_products.data:
            product = item["product"]
            formatted_product = {
                "id": product["id"],
                "name": product["name"],
                "artist": product["artist"],
                "valor": float(product["valor"]),
                "quantity": item["quantity"],
                "image_path": product.get("image_path")
            }
            formatted_products.append(formatted_product)
        
        print(f'Produtos formatados: {formatted_products}')
        return formatted_products
        
    except Exception as e:
        print(f'ERRO em get_cart_products: {str(e)}')
        print(f'Tipo do erro: {type(e)}')
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar produtos do carrinho: {str(e)}")

class RemoveProductFromCartRequest(BaseModel):
    productId: int

@app.post("/api/remove_product_from_cart")
def remove_product_from_cart(
    removeProduct: RemoveProductFromCartRequest,
    current_user: dict = Depends(get_current_user)
):
    """Remover produto do carrinho (diminui quantidade ou remove completamente)"""
    try:
        print('=== DEBUG REMOVE_PRODUCT_FROM_CART ===')
        print(f'Dados recebidos: productId={removeProduct.productId}')
        print(f'Usuário atual: {current_user}')

        from supabase_client import supabase
        
        user_id = current_user["id"]
        print(f'User ID: {user_id}')
        
        # Buscar carrinho do usuário
        print('Buscando carrinho do usuário...')
        cart_response = supabase.table("shoppingcarts").select("*").eq("user_id", user_id).execute()
        print(f'Resposta do carrinho: {cart_response.data}')
        
        if not cart_response.data:
            print('Carrinho não encontrado')
            raise HTTPException(status_code=404, detail="Carrinho não encontrado")
        
        cart_id = cart_response.data[0]["id"]
        print(f'Carrinho encontrado: {cart_id}')
        
        # Buscar produto no carrinho
        print('Buscando produto no carrinho...')
        cart_product_response = supabase.table("shoppingcart_products").select("*").eq("shoppingcart_id", cart_id).eq("product_id", removeProduct.productId).execute()
        print(f'Produto no carrinho: {cart_product_response.data}')
        
        if not cart_product_response.data:
            print('Produto não encontrado no carrinho')
            raise HTTPException(status_code=404, detail="Produto não encontrado no carrinho")
        
        cart_product = cart_product_response.data[0]
        current_quantity = cart_product["quantity"]
        print(f'Quantidade atual: {current_quantity}')
        
        if current_quantity > 1:
            # Diminuir quantidade em 1
            print('Diminuindo quantidade em 1...')
            new_quantity = current_quantity - 1
            update_response = supabase.table("shoppingcart_products").update({
                "quantity": new_quantity
            }).eq("shoppingcart_id", cart_id).eq("product_id", removeProduct.productId).execute()
            print(f'Quantidade atualizada: {update_response.data}')
            
            return {
                "message": "Quantidade do produto diminuída",
                "action": "quantity_decreased",
                "new_quantity": new_quantity,
                "cart_product": update_response.data[0]
            }
        else:
            # Remover produto completamente (quantidade = 1)
            print('Removendo produto completamente...')
            delete_response = supabase.table("shoppingcart_products").delete().eq("shoppingcart_id", cart_id).eq("product_id", removeProduct.productId).execute()
            print(f'Produto removido: {delete_response.data}')
            
            return {
                "message": "Produto removido do carrinho",
                "action": "product_removed",
                "removed_product": cart_product
            }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f'ERRO em remove_product_from_cart: {str(e)}')
        print(f'Tipo do erro: {type(e)}')
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao remover produto do carrinho: {str(e)}")

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

# Endpoint para verificar estrutura das tabelas (apenas para debug)
@app.get("/api/debug/check_tables")
def debug_check_tables(db: Session = Depends(get_db_session)):
    """Verifica se as tabelas existem"""
    try:
        # Testar se consegue fazer query nas tabelas
        users_count = db.query(User).count()
        products_count = db.query(Product).count()
        
        try:
            carts_count = db.query(ShoppingCart).count()
        except Exception as e:
            carts_count = f"ERRO: {str(e)}"
        
        try:
            cart_products_count = db.query(ShoppingCartProduct).count()
        except Exception as e:
            cart_products_count = f"ERRO: {str(e)}"
        
        return {
            "users": users_count,
            "products": products_count,
            "shopping_carts": carts_count,
            "cart_products": cart_products_count
        }
    except Exception as e:
        return {"error": str(e)}

# ===== ENDPOINTS DE DEBUG PARA PRODUÇÃO =====

@app.get("/api/debug/test_supabase_connection")
async def debug_test_supabase_connection(current_user: dict = Depends(get_current_user)):
    """Testar conexão com Supabase em produção"""
    try:
        print('[DEBUG PRODUÇÃO] Testando conexão com Supabase...')
        
        # Testar busca simples
        products_response = supabase.table("products").select("id, name").limit(1).execute()
        print(f'[DEBUG] Produtos response: {products_response}')
        
        # Testar busca de usuário
        user_response = supabase.table("users").select("*").eq("id", current_user['id']).execute()
        print(f'[DEBUG] User response: {user_response}')
        
        # Testar busca de carrinho
        cart_response = supabase.table("shoppingcarts").select("*").eq("user_id", current_user['id']).execute()
        print(f'[DEBUG] Cart response: {cart_response}')
        
        return {
            "environment": "production" if "herokuapp" in str(os.environ.get("REQUEST_URI", "")) else "local",
            "user_id": current_user['id'],
            "products_count": len(products_response.data) if products_response.data else 0,
            "user_found": len(user_response.data) > 0 if user_response.data else False,
            "cart_found": len(cart_response.data) > 0 if cart_response.data else False,
            "supabase_url": os.environ.get("SUPABASE_URL", "NOT_SET")[:50] + "...",
            "supabase_key": "SET" if os.environ.get("SUPABASE_KEY") else "NOT_SET"
        }
        
    except Exception as e:
        print(f'[DEBUG] Erro no teste de conexão: {str(e)}')
        import traceback
        traceback.print_exc()
        return {"error": str(e), "traceback": traceback.format_exc()}

@app.post("/api/debug/test_cart_creation")
async def debug_test_cart_creation(current_user: dict = Depends(get_current_user)):
    """Testar criação de carrinho especificamente"""
    try:
        print('[DEBUG PRODUÇÃO] Testando criação de carrinho...')
        
        user_id = current_user["id"]
        print(f'[DEBUG] User ID: {user_id}')
        
        # Verificar se carrinho já existe
        existing_cart = supabase.table("shoppingcarts").select("*").eq("user_id", user_id).execute()
        print(f'[DEBUG] Carrinho existente: {existing_cart}')
        
        if existing_cart.data:
            return {
                "message": "Carrinho já existe",
                "cart": existing_cart.data[0],
                "environment": "production" if "herokuapp" in str(os.environ.get("REQUEST_URI", "")) else "local"
            }
        
        # Tentar criar carrinho
        cart_data = {"user_id": user_id}
        print(f'[DEBUG] Dados do carrinho: {cart_data}')
        
        create_response = supabase.table("shoppingcarts").insert(cart_data).execute()
        print(f'[DEBUG] Response da criação: {create_response}')
        
        return {
            "message": "Carrinho criado com sucesso",
            "cart": create_response.data[0] if create_response.data else None,
            "environment": "production" if "herokuapp" in str(os.environ.get("REQUEST_URI", "")) else "local"
        }
        
    except Exception as e:
        print(f'[DEBUG] Erro na criação do carrinho: {str(e)}')
        import traceback
        traceback.print_exc()
        return {"error": str(e), "traceback": traceback.format_exc()}

@app.get("/api/debug/test_cart_detailed")
async def debug_test_cart_detailed(current_user: dict = Depends(get_current_user)):
    """Debug detalhado do carrinho em produção"""
    try:
        print('[DEBUG CARRINHO] Iniciando teste detalhado...')
        
        user_id = current_user["id"]
        print(f'[DEBUG] User ID: {user_id}')
        
        # Testar se consegue acessar tabela shoppingcarts
        try:
            cart_search = supabase.table("shoppingcarts").select("*").eq("user_id", user_id).execute()
            print(f'[DEBUG] Cart search response: {cart_search}')
        except Exception as cart_error:
            print(f'[DEBUG] Erro ao buscar carrinho: {str(cart_error)}')
            cart_search = {"error": str(cart_error), "data": None}
        
        # Testar criar carrinho se não existir
        cart_creation_result = None
        if not cart_search.get("data"):
            try:
                cart_data = {"user_id": user_id}
                cart_creation = supabase.table("shoppingcarts").insert(cart_data).execute()
                print(f'[DEBUG] Cart creation response: {cart_creation}')
                cart_creation_result = cart_creation
            except Exception as create_error:
                print(f'[DEBUG] Erro ao criar carrinho: {str(create_error)}')
                cart_creation_result = {"error": str(create_error)}
        
        # Testar buscar produtos do carrinho
        cart_products_result = None
        if cart_search.get("data") or cart_creation_result:
            try:
                cart_id = cart_search["data"][0]["id"] if cart_search.get("data") else cart_creation_result["data"][0]["id"]
                cart_products = supabase.table("shoppingcart_products").select("*, product:products(*)").eq("shoppingcart_id", cart_id).execute()
                print(f'[DEBUG] Cart products response: {cart_products}')
                cart_products_result = cart_products
            except Exception as products_error:
                print(f'[DEBUG] Erro ao buscar produtos do carrinho: {str(products_error)}')
                cart_products_result = {"error": str(products_error)}
        
        return {
            "user_id": user_id,
            "cart_search": cart_search,
            "cart_creation": cart_creation_result,
            "cart_products": cart_products_result,
            "environment": "production" if "herokuapp" in str(os.environ.get("HTTP_HOST", "")) else "local"
        }
        
    except Exception as e:
        print(f'[DEBUG] Erro geral no teste: {str(e)}')
        import traceback
        traceback.print_exc()
        return {"error": str(e), "traceback": traceback.format_exc()}

# ===== ROTAS DE FRONTEND (DEVEM SER AS ÚLTIMAS) =====
# Rota para servir o frontend React
@app.get("/")
@app.get("/{full_path:path}")
def serve_frontend(full_path: str = None):
    # Caminho para o arquivo index.html do frontend buildado
    frontend_path = Path(os.getcwd()) / "FrontEnd" / "dist" / "index.html"
    
    if frontend_path.exists():
        return FileResponse(frontend_path)
    else:
        # Fallback para desenvolvimento - retorna informações da API
        return {"message": "Rock Symphony API - Marketplace de CDs de Rock", "version": "1.0.0", "note": "Frontend não encontrado. Execute 'npm run build' no FrontEnd para gerar os arquivos."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
