from datetime import date
import json
import csv
import random
import string
import time
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
        # from supabase_client import supabase (removido para evitar erro no Heroku)

def get_supabase_client():
    """Função helper para obter cliente Supabase (funciona local e Heroku)"""
    return supabase

# Lista de países disponíveis
COUNTRY_OPTIONS = [
    'Brasil',
    'Estados Unidos',
    'Reino Unido',
    'Alemanha',
    'França',
    'Japão',
    'Canadá',
    'Austrália',
    'Argentina',
    'México',
    'Holanda',
    'Suécia',
    'Noruega',
    'Dinamarca',
    'Finlândia',
    'Itália',
    'Espanha',
    'Portugal',
    'Bélgica',
    'Áustria',
    'Suíça',
    'Polônia',
    'República Tcheca',
    'Hungria',
    'Grécia',
    'Turquia',
    'Rússia',
    'China',
    'Coreia do Sul',
    'Índia',
    'Tailândia',
    'Singapura',
    'Nova Zelândia',
    'África do Sul',
    'Chile',
    'Colômbia',
    'Peru',
    'Uruguai',
    'Paraguai',
    'Bolívia',
    'Equador',
    'Venezuela',
    'Cuba',
    'Jamaica',
    'Outro'
]

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
        
        # CORREÇÃO: Usar Supabase diretamente ao invés de SQLAlchemy
        print("Executando query no Supabase...")
        user_response = supabase.table("users").select("*").eq("id", current_user["id"]).execute()
        print(f"Query executada. Resposta: {user_response}")
        
        if user_response.data and len(user_response.data) > 0:
            user_data = user_response.data[0]
            print(f"Usuário encontrado: {user_data}")
            
            # Criar objeto User-like para compatibilidade
            class UserLike:
                def __init__(self, data):
                    self.id = data["id"]
                    self.usuario = data.get("usuario", "")
                    self.email = data.get("email", "")
                    self.is_admin = data.get("is_admin", False)
            
            user = UserLike(user_data)
            print(f"Objeto User recuperado e instanciado: {user.id}")
            return user
        else:
            print("Usuário não encontrado no Supabase, criando novo...")
            # Se não encontrar, criar um novo usuário com os dados do Supabase
            user_data = {
                "id": current_user["id"],
                "usuario": current_user.get("usuario", ""),
                "email": current_user.get("email", ""),
                "is_admin": current_user.get("is_admin", False)
            }
            print(f"Dados para criar usuário: {user_data}")
            
            # Inserir no Supabase
            insert_response = supabase.table("users").insert(user_data).execute()
            print(f"Usuário inserido: {insert_response}")
            
            if insert_response.data:
                # Criar objeto User-like
                class UserLike:
                    def __init__(self, data):
                        self.id = data["id"]
                        self.usuario = data.get("usuario", "")
                        self.email = data.get("email", "")
                        self.is_admin = data.get("is_admin", False)
                
                user = UserLike(insert_response.data[0])
                print(f"Usuário criado: {user.id}")
                return user
            else:
                raise Exception("Erro ao criar usuário no Supabase")
        
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

@app.get("/api/countries")
async def get_countries():
    """Obter lista de países disponíveis"""
    return {"countries": COUNTRY_OPTIONS}

@app.get("/api/products")
async def get_available_products(current_user: dict = Depends(get_current_user_optional)):
    """Buscar todos os produtos disponíveis - acesso público"""
    user_id = current_user['id'] if current_user else "anônimo"
    print(f"[DEBUG] Buscando produtos para usuário: {user_id}")
    
    try:
        # Buscar produtos no Supabase
        response = supabase.table("products").select("*").execute()
        
        print(f"[DEBUG] Produtos encontrados no Supabase: {len(response.data) if response.data else 0}")
        
        if response.data:
            print(f"[DEBUG] Primeiro produto: {response.data[0]}")
            return response.data
        else:
            print("[DEBUG] Nenhum produto encontrado no Supabase")
            return []  # Retornar lista vazia ao invés de erro para usuários não logados
            
    except Exception as e:
        print(f"[DEBUG] Erro ao buscar produtos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar produtos: {str(e)}")

class ProductCreate(BaseModel):
    name: str
    artist: str
    description: str
    valor: float
    remaining: int
    reference_code: str = ""
    stamp: str = ""
    release_year: int = None
    country: str = ""

@app.post("/api/products")
async def create_new_product(
    name: str = Form(...),
    artist: str = Form(...),
    description: str = Form(...),
    valor: float = Form(...),
    remaining: int = Form(...),
    reference_code: str = Form(""),
    stamp: str = Form(""),
    release_year: int = Form(None),
    country: str = Form(""),
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
                file_extension = file.filename.split(".")[-1].lower() if "." in file.filename else "jpg"
                file_name = f"{name.replace(' ', '_')}_{int(datetime.now().timestamp())}.{file_extension}"
                
                print(f"[DEBUG] Fazendo upload da imagem: {file_name}")
                
                # Mapear extensões para MIME types corretos
                mime_types = {
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                    'png': 'image/png',
                    'gif': 'image/gif',
                    'webp': 'image/webp'
                }
                
                content_type = mime_types.get(file_extension, 'image/jpeg')
                print(f"[DEBUG] Content-Type: {content_type}")
                
                # Upload para o Supabase Storage
                storage_response = supabase.storage.from_("product-images").upload(
                    file_name, 
                    file_content,
                    file_options={"content-type": content_type}
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
            "image_path": image_path,
            "reference_code": reference_code,
            "stamp": stamp,
            "release_year": release_year,
            "country": country
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
    reference_code: str = ""
    stamp: str = ""
    release_year: int = None
    country: str = ""

@app.put("/api/products/{product_id}")
async def edit_product(
    product_id: int,
    name: str = Form(...),
    artist: str = Form(...),
    description: str = Form(...),
    valor: float = Form(...),
    remaining: int = Form(...),
    reference_code: str = Form(""),
    stamp: str = Form(""),
    release_year: int = Form(None),
    country: str = Form(""),
    file: UploadFile = File(None),  # Imagem opcional
    current_user: dict = Depends(get_current_admin_user)
):
    """Editar um produto existente (apenas admin)"""
    try:
        print(f"[DEBUG] Editando produto ID: {product_id}")
        print(f"[DEBUG] Dados recebidos: name={name}, artist={artist}, valor={valor}, remaining={remaining}")
        print(f"[DEBUG] Novos campos: reference_code={reference_code}, stamp={stamp}, release_year={release_year}, country={country}")
        print(f"[DEBUG] Nova imagem: {file.filename if file else 'Nenhuma'}")
        
        # Buscar produto atual para obter a imagem antiga
        current_product = supabase.table("products").select("*").eq("id", product_id).execute()
        
        if not current_product.data:
            raise HTTPException(status_code=404, detail="Produto não encontrado")
        
        old_image_path = current_product.data[0].get("image_path")
        new_image_path = old_image_path  # Manter a imagem atual por padrão
        
        # Se uma nova imagem foi enviada, fazer upload
        if file and file.filename:
            print(f"[DEBUG] Processando upload da nova imagem: {file.filename}")
            
            # Gerar nome único para a nova imagem
            file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else 'jpg'
            unique_filename = f"{name.replace(' ', '_')}_{int(time.time())}.{file_extension}"
            
            print(f"[DEBUG] Nome único gerado: {unique_filename}")
            
            # Fazer upload da nova imagem
            file_content = await file.read()
            
            # Mapear extensões para MIME types corretos
            mime_types = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'gif': 'image/gif',
                'webp': 'image/webp'
            }
            
            content_type = mime_types.get(file_extension, 'image/jpeg')
            print(f"[DEBUG] Content-Type: {content_type}")
            
            try:
                # Upload para o bucket do Supabase
                upload_response = supabase.storage.from_("product-images").upload(
                    unique_filename, 
                    file_content,
                    {"content-type": content_type}
                )
                
                print(f"[DEBUG] Upload response: {upload_response}")
                
                # Obter URL pública da nova imagem
                public_url_response = supabase.storage.from_("product-images").get_public_url(unique_filename)
                new_image_path = public_url_response
                
                print(f"[DEBUG] Nova URL pública: {new_image_path}")
                
                # Deletar a imagem antiga do bucket (se existir e for diferente da nova)
                if old_image_path and old_image_path != new_image_path:
                    try:
                        # Extrair nome do arquivo da URL antiga
                        old_filename = old_image_path.split('/')[-1] if '/' in old_image_path else old_image_path
                        if old_filename and old_filename != unique_filename:
                            delete_response = supabase.storage.from_("product-images").remove([old_filename])
                            print(f"[DEBUG] Imagem antiga deletada: {old_filename}")
                    except Exception as e:
                        print(f"[DEBUG] Erro ao deletar imagem antiga: {e}")
                        # Não falhar se não conseguir deletar a imagem antiga
                
            except Exception as e:
                print(f"[DEBUG] Erro no upload: {e}")
                raise HTTPException(status_code=500, detail=f"Erro no upload da imagem: {str(e)}")
        
        # Atualizar produto no Supabase
        update_data = {
            "name": name,
            "artist": artist,
            "description": description,
            "valor": valor,
            "remaining": remaining,
            "image_path": new_image_path,
            "reference_code": reference_code,
            "stamp": stamp,
            "release_year": release_year,
            "country": country
        }
        
        print(f"[DEBUG] Atualizando produto com dados: {update_data}")
        
        response = supabase.table("products").update(update_data).eq("id", product_id).execute()
        
        if response.data:
            return {"message": f"Produto '{name}' atualizado com sucesso!"}
        else:
            raise HTTPException(status_code=404, detail="Produto não encontrado")
        
    except Exception as e:
        print(f"[DEBUG] Erro ao editar produto: {str(e)}")
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

# ===== ENDPOINTS DE ENDEREÇOS =====

from pydantic import BaseModel
from typing import Optional

class AddressCreate(BaseModel):
    cep: str
    street: str
    number: str
    complement: Optional[str] = None
    neighborhood: str
    city: str
    state: str
    country: str = "Brasil"
    receiver_name: str
    is_default: bool = False

class AddressUpdate(BaseModel):
    cep: Optional[str] = None
    street: Optional[str] = None
    number: Optional[str] = None
    complement: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    receiver_name: Optional[str] = None
    is_default: Optional[bool] = None

@app.get("/api/viacep/{cep}")
async def get_address_by_cep(cep: str):
    """Buscar endereço pelo CEP usando API do ViaCEP"""
    try:
        import requests
        # Remove caracteres não numéricos do CEP
        clean_cep = ''.join(filter(str.isdigit, cep))
        
        if len(clean_cep) != 8:
            raise HTTPException(status_code=400, detail="CEP deve conter 8 dígitos")
        
        # Consulta a API do ViaCEP
        response = requests.get(f"https://viacep.com.br/ws/{clean_cep}/json/")
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Erro ao consultar CEP")
        
        data = response.json()
        
        if 'erro' in data:
            raise HTTPException(status_code=404, detail="CEP não encontrado")
        
        return {
            "cep": data.get("cep", ""),
            "street": data.get("logradouro", ""),
            "neighborhood": data.get("bairro", ""),
            "city": data.get("localidade", ""),
            "state": data.get("uf", ""),
            "country": "Brasil"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar CEP: {str(e)}")

@app.post("/api/addresses")
async def create_address(
    address: AddressCreate,
    current_user: dict = Depends(get_current_user)
):
    """Criar um novo endereço para o usuário"""
    try:
        user_id = current_user["id"]
        
        # Construir endereço completo
        full_address = f"{address.street}, {address.number}"
        if address.complement:
            full_address += f", {address.complement}"
        full_address += f", {address.neighborhood}, {address.city} - {address.state}, {address.cep}"
        
        # Se este endereço está sendo marcado como padrão, desmarcar outros
        if address.is_default:
            # Desmarcar outros endereços como padrão
            supabase.table("addresses").update({"is_default": False}).eq("user_id", user_id).execute()
        
        # Criar novo endereço
        address_data = {
            "user_id": user_id,
            "cep": address.cep,
            "street": address.street,
            "number": address.number,
            "complement": address.complement,
            "neighborhood": address.neighborhood,
            "city": address.city,
            "state": address.state,
            "country": address.country,
            "receiver_name": address.receiver_name,
            "full_address": full_address,
            "is_default": address.is_default
        }
        
        response = supabase.table("addresses").insert(address_data).execute()
        
        if response.data:
            return {"message": "Endereço criado com sucesso!", "address": response.data[0]}
        else:
            raise HTTPException(status_code=500, detail="Erro ao criar endereço")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar endereço: {str(e)}")

@app.get("/api/addresses")
async def get_user_addresses(
    current_user: dict = Depends(get_current_user)
):
    """Obter todos os endereços do usuário"""
    try:
        user_id = current_user["id"]
        
        response = supabase.table("addresses").select("*").eq("user_id", user_id).order("is_default", desc=True).execute()
        
        return response.data if response.data else []
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar endereços: {str(e)}")

@app.put("/api/addresses/{address_id}")
async def update_address(
    address_id: int,
    address: AddressUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Atualizar um endereço existente"""
    try:
        user_id = current_user["id"]
        
        # Verificar se o endereço pertence ao usuário
        existing_address = supabase.table("addresses").select("*").eq("id", address_id).eq("user_id", user_id).execute()
        
        if not existing_address.data:
            raise HTTPException(status_code=404, detail="Endereço não encontrado")
        
        # Preparar dados para atualização
        update_data = {}
        for field, value in address.dict(exclude_unset=True).items():
            if value is not None:
                update_data[field] = value
        
        # Se este endereço está sendo marcado como padrão, desmarcar outros
        if address.is_default:
            supabase.table("addresses").update({"is_default": False}).eq("user_id", user_id).execute()
        
        # Reconstruir endereço completo se necessário
        if any(field in update_data for field in ["street", "number", "complement", "neighborhood", "city", "state", "cep"]):
            old_data = existing_address.data[0]
            # Usar dados novos ou antigos para construir o endereço completo
            street = update_data.get("street", old_data["street"])
            number = update_data.get("number", old_data["number"])
            complement = update_data.get("complement", old_data.get("complement"))
            neighborhood = update_data.get("neighborhood", old_data["neighborhood"])
            city = update_data.get("city", old_data["city"])
            state = update_data.get("state", old_data["state"])
            cep = update_data.get("cep", old_data["cep"])
            
            full_address = f"{street}, {number}"
            if complement:
                full_address += f", {complement}"
            full_address += f", {neighborhood}, {city} - {state}, {cep}"
            update_data["full_address"] = full_address
        
        response = supabase.table("addresses").update(update_data).eq("id", address_id).eq("user_id", user_id).execute()
        
        if response.data:
            return {"message": "Endereço atualizado com sucesso!", "address": response.data[0]}
        else:
            raise HTTPException(status_code=500, detail="Erro ao atualizar endereço")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar endereço: {str(e)}")

@app.delete("/api/addresses/{address_id}")
async def delete_address(
    address_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Deletar um endereço"""
    try:
        user_id = current_user["id"]
        
        # Verificar se o endereço pertence ao usuário
        existing_address = supabase.table("addresses").select("*").eq("id", address_id).eq("user_id", user_id).execute()
        
        if not existing_address.data:
            raise HTTPException(status_code=404, detail="Endereço não encontrado")
        
        response = supabase.table("addresses").delete().eq("id", address_id).eq("user_id", user_id).execute()
        
        return {"message": "Endereço deletado com sucesso!"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar endereço: {str(e)}")

@app.post("/api/addresses/{address_id}/set-default")
async def set_default_address(
    address_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Definir um endereço como padrão"""
    try:
        user_id = current_user["id"]
        
        # Verificar se o endereço pertence ao usuário
        existing_address = supabase.table("addresses").select("*").eq("id", address_id).eq("user_id", user_id).execute()
        
        if not existing_address.data:
            raise HTTPException(status_code=404, detail="Endereço não encontrado")
        
        # Desmarcar todos os endereços como padrão
        supabase.table("addresses").update({"is_default": False}).eq("user_id", user_id).execute()
        
        # Marcar o endereço selecionado como padrão
        response = supabase.table("addresses").update({"is_default": True}).eq("id", address_id).eq("user_id", user_id).execute()
        
        return {"message": "Endereço definido como padrão!"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao definir endereço padrão: {str(e)}")

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
        #    # Usar o cliente já importado no início do arquivo
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
        
        # Usar o cliente já importado no início do arquivo
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

        # Usar o cliente já importado no início do arquivo
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
    order_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Criar pedido a partir do carrinho"""
    try:
        print("=== DEBUG HANDLE_CHECKOUT ===")
        print(f"Dados recebidos: {order_data}")
        print(f"Usuário: {current_user['id']}")
        
        user_id = current_user["id"]
        
        # Verificar se o endereço foi fornecido
        address_id = order_data.get("address_id")
        if not address_id:
            raise HTTPException(status_code=400, detail="Endereço de entrega é obrigatório")

        # Verificar se o endereço pertence ao usuário
        print(f"Verificando endereço {address_id} para usuário {user_id}")
        address_response = supabase.table("addresses").select("*").eq("id", address_id).eq("user_id", user_id).execute()
        if not address_response.data:
            raise HTTPException(status_code=404, detail="Endereço não encontrado ou não pertence ao usuário")

        # Buscar carrinho do usuário
        print("Buscando carrinho do usuário...")
        cart_response = supabase.table("shoppingcarts").select("*").eq("user_id", user_id).execute()
        
        if not cart_response.data:
            raise HTTPException(status_code=404, detail="Carrinho não encontrado")
        
        cart_id = cart_response.data[0]["id"]
        print(f"Carrinho encontrado: {cart_id}")

        # Obter produtos do carrinho
        print("Buscando produtos do carrinho...")
        cart_products_response = supabase.table("shoppingcart_products").select(
            "*, product:products(*)"
        ).eq("shoppingcart_id", cart_id).execute()

        if not cart_products_response.data:
            raise HTTPException(status_code=400, detail="Carrinho está vazio")

        print(f"Produtos no carrinho: {len(cart_products_response.data)}")

        # Calcular total
        total_value = 0
        for cart_item in cart_products_response.data:
            product = cart_item["product"]
            quantity = cart_item["quantity"]
            total_value += float(product["valor"]) * quantity

        print(f"Total calculado: {total_value}")

        # Criar o pedido no Supabase
        print("Criando pedido...")
        order_data_db = {
            "user_id": user_id,
            "address_id": address_id,
            "total_amount": total_value,
            "pending": True,
            "active": True
        }
        
        order_response = supabase.table("orders").insert(order_data_db).execute()
        
        if not order_response.data:
            raise HTTPException(status_code=500, detail="Erro ao criar pedido")
        
        new_order_id = order_response.data[0]["id"]
        print(f"Pedido criado: {new_order_id}")

        # Adicionar produtos ao pedido
        print("Adicionando produtos ao pedido...")
        for cart_item in cart_products_response.data:
            product = cart_item["product"]
            quantity = cart_item["quantity"]
            
            order_product_data = {
                "order_id": new_order_id,
                "product_id": product["id"],
                "quantity": quantity,
                "price_at_time": float(product["valor"])
            }
            
            supabase.table("order_products").insert(order_product_data).execute()

        # Limpar carrinho
        print("Limpando carrinho...")
        supabase.table("shoppingcart_products").delete().eq("shoppingcart_id", cart_id).execute()
        
        print("Pedido criado com sucesso!")
        return {
            "message": "Pedido criado com sucesso",
            "order_id": new_order_id,
            "total_amount": total_value,
            "redirect_to": "/minhas-reservas",
            "order_details": {
                "id": new_order_id,
                "user_id": user_id,
                "address_id": address_id,
                "total_amount": total_value,
                "pending": True,
                "active": True,
                "created_at": order_response.data[0].get("created_at")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao criar pedido: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao criar pedido: {str(e)}")

@app.get("/api/orders")
async def get_user_orders(
    current_user: dict = Depends(get_current_user)
):
    """Obter pedidos do usuário usando Supabase"""
    try:
        user_id = current_user["id"]
        
        # Buscar pedidos do usuário
        orders_response = supabase.table("orders").select(
            "*, order_products(*, product:products(*))"
        ).eq("user_id", user_id).execute()
        
        result = []
        for order in orders_response.data:
            products = []
            total_value = 0
            
            for order_product in order.get("order_products", []):
                product = order_product["product"]
                quantity = order_product["quantity"]
                price_at_time = float(order_product.get("price_at_time", product["valor"]))
                
                print(f"[DEBUG] Produto no pedido {order['id']}: {product.get('name', 'N/A')}")
                print(f"  image_path: {product.get('image_path', 'N/A')}")
                
                products.append({
                    "id": product["id"],  # Adicionar ID do produto
                    "name": product["name"],
                    "artist": product["artist"],
                    "quantity": quantity,
                    "valor": price_at_time,
                    "image_path": product.get("image_path")  # Adicionar image_path
                })
                total_value += price_at_time * quantity
            
            result.append({
                "id": order["id"],
                "order_date": order["order_date"],
                "pending": order["pending"],
                "active": order["active"],
                "payment_link": order.get("payment_link"),  # Adicionar payment_link
                "total_amount": order.get("total_amount", total_value),  # Usar total_amount do banco ou calculado
                "products": products
            })
        
        return result
        
    except Exception as e:
        print(f"Erro ao buscar pedidos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar pedidos: {str(e)}")
    
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

@app.get("/api/usuarios")
async def list_usuarios(
    skip: int = 0, 
    limit: int = 100, 
    current_user: dict = Depends(get_current_admin_user)
):
    """Listar usuários do Supabase (apenas admin)"""
    try:
        print(f"[DEBUG] Buscando usuários no Supabase...")
        
        # Buscar usuários da nossa tabela users (que já contém o email)
        response = supabase.table("users").select("*").range(skip, skip + limit - 1).execute()
        
        print(f"[DEBUG] Usuários encontrados: {len(response.data) if response.data else 0}")
        
        if response.data:
            # Adicionar username para compatibilidade com o frontend
            for user in response.data:
                user["username"] = user.get("usuario", "")
            
            return response.data
        else:
            return []
            
    except Exception as e:
        print(f"[DEBUG] Erro ao buscar usuários: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar usuários: {str(e)}")

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

# Pydantic models para usuários
class UsuarioCreate(BaseModel):
    email: str
    password: str
    username: str = ""
    is_admin: bool = False

class UsuarioUpdate(BaseModel):
    username: str = ""
    is_admin: bool = False

@app.post("/api/usuarios")
async def create_usuario(
    usuario: UsuarioCreate,
    current_user: dict = Depends(get_current_admin_user)
):
    """Criar novo usuário (apenas admin)"""
    try:
        print(f"[DEBUG] Criando usuário: {usuario.email}")
        
        # Criar usuário no Supabase Auth
        auth_response = supabase.auth.admin.create_user({
            "email": usuario.email,
            "password": usuario.password,
            "user_metadata": {
                "username": usuario.username,
                "is_admin": usuario.is_admin
            }
        })
        
        if auth_response.user:
            # Criar entrada na tabela users incluindo o email
            user_data = {
                "id": auth_response.user.id,
                "usuario": usuario.username,
                "email": usuario.email,  # Salvar email na nossa tabela
                "is_admin": usuario.is_admin
            }
            
            table_response = supabase.table("users").insert(user_data).execute()
            
            return {"message": "Usuário criado com sucesso", "user": table_response.data[0]}
        else:
            raise HTTPException(status_code=500, detail="Erro ao criar usuário no Supabase Auth")
            
    except Exception as e:
        print(f"[DEBUG] Erro ao criar usuário: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar usuário: {str(e)}")

@app.put("/api/usuarios/{user_id}")
async def update_usuario(
    user_id: str,
    usuario: UsuarioUpdate,
    current_user: dict = Depends(get_current_admin_user)
):
    """Atualizar usuário (apenas admin)"""
    try:
        print(f"[DEBUG] Atualizando usuário: {user_id}")
        
        # Atualizar na tabela users
        response = supabase.table("users").update({
            "usuario": usuario.username,
            "is_admin": usuario.is_admin
        }).eq("id", user_id).execute()
        
        if response.data:
            return {"message": "Usuário atualizado com sucesso", "user": response.data[0]}
        else:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
            
    except Exception as e:
        print(f"[DEBUG] Erro ao atualizar usuário: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar usuário: {str(e)}")

@app.delete("/api/usuarios/{user_id}")
async def delete_usuario(
    user_id: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """Deletar usuário (apenas admin)"""
    try:
        print(f"[DEBUG] Deletando usuário: {user_id}")
        
        # Buscar usuário primeiro para obter nome
        user_response = supabase.table("users").select("*").eq("id", user_id).execute()
        
        if not user_response.data:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        user = user_response.data[0]
        
        # Deletar da tabela users
        delete_response = supabase.table("users").delete().eq("id", user_id).execute()
        
        # Tentar deletar do Supabase Auth (pode falhar se o usuário não existir mais)
        try:
            supabase.auth.admin.delete_user(user_id)
        except Exception as auth_error:
            print(f"[DEBUG] Erro ao deletar do Auth (ignorado): {str(auth_error)}")
        
        return {"message": f"Usuário '{user.get('usuario', user_id)}' deletado com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[DEBUG] Erro ao deletar usuário: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao deletar usuário: {str(e)}")

@app.post("/api/register")
async def register_usuario(
    usuario: UsuarioCreate
):
    """Registrar novo usuário (público)"""
    try:
        print(f"[DEBUG] Registrando usuário: {usuario.email}")
        
        # Criar usuário no Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": usuario.email,
            "password": usuario.password,
            "options": {
                "data": {
                    "username": usuario.username,
                    "is_admin": False  # Usuários cadastrados pelo público não são admin
                }
            }
        })
        
        if auth_response.user:
            # Criar entrada na tabela users incluindo o email
            user_data = {
                "id": auth_response.user.id,
                "usuario": usuario.username or usuario.email.split('@')[0],  # Se não tiver username, usar parte do email
                "email": usuario.email,
                "is_admin": False  # Usuários cadastrados pelo público não são admin
            }
            
            table_response = supabase.table("users").insert(user_data).execute()
            
            return {
                "message": "Usuário registrado com sucesso! Verifique seu email para confirmar a conta.",
                "user": {
                    "id": auth_response.user.id,
                    "email": auth_response.user.email,
                    "username": usuario.username
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Erro ao registrar usuário no Supabase Auth")
            
    except Exception as e:
        print(f"[DEBUG] Erro ao registrar usuário: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao registrar usuário: {str(e)}")

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

@app.get("/api/debug/test_user_email/{user_id}")
async def debug_test_user_email(
    user_id: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """Debug: testar busca de email específico"""
    try:
        print(f"[DEBUG] Testando busca de email para usuário: {user_id}")
        
        # Método 1: Admin API
        try:
            auth_response = supabase.auth.admin.get_user_by_id(user_id)
            print(f"[DEBUG] Admin API response: {auth_response}")
            
            if auth_response and hasattr(auth_response, 'user') and auth_response.user:
                email_admin = auth_response.user.email
                print(f"[DEBUG] Email via Admin API: {email_admin}")
            else:
                email_admin = "N/A - Admin API failed"
        except Exception as e:
            email_admin = f"ERRO Admin API: {str(e)}"
            print(f"[DEBUG] Erro Admin API: {str(e)}")
        
        # Método 2: Buscar na tabela users
        try:
            user_response = supabase.table("users").select("*").eq("id", user_id).execute()
            print(f"[DEBUG] User table response: {user_response}")
            user_data = user_response.data[0] if user_response.data else None
        except Exception as e:
            user_data = f"ERRO User table: {str(e)}"
            print(f"[DEBUG] Erro User table: {str(e)}")
        
        return {
            "user_id": user_id,
            "email_admin_api": email_admin,
            "user_table_data": user_data,
            "supabase_url": os.environ.get("SUPABASE_URL", "NOT_SET")[:50] + "...",
            "has_service_key": bool(os.environ.get("SUPABASE_SERVICE_KEY"))
        }
        
    except Exception as e:
        print(f"[DEBUG] Erro geral: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "traceback": traceback.format_exc()}

# ===== ENDPOINTS DE PEDIDOS SUPABASE =====

@app.post("/api/create_order")
async def create_order_supabase(
    current_user: dict = Depends(get_current_user)
):
    """Criar pedido a partir do carrinho do usuário no Supabase"""
    try:
        user_id = current_user["id"]
        print(f"[DEBUG] Criando pedido para usuário: {user_id}")
        
        # Primeiro, buscar o carrinho do usuário
        cart_response = supabase.table("shoppingcarts").select("*").eq("user_id", user_id).execute()
        
        if not cart_response.data:
            raise HTTPException(status_code=400, detail="Carrinho não encontrado")
        
        cart_id = cart_response.data[0]["id"]
        print(f"[DEBUG] Carrinho encontrado: {cart_id}")
        
        # Agora buscar produtos no carrinho usando o cart_id
        cart_products_response = supabase.table("shoppingcart_products").select("*, products(*)").eq("shoppingcart_id", cart_id).execute()
        
        if not cart_products_response.data:
            raise HTTPException(status_code=400, detail="Carrinho está vazio")
        
        cart_products = cart_products_response.data
        print(f"[DEBUG] Produtos no carrinho: {len(cart_products)}")
        
        # Calcular total
        total_amount = sum(item["products"]["valor"] * item["quantity"] for item in cart_products)
        print(f"[DEBUG] Total do pedido: R$ {total_amount}")
        
        # Criar pedido
        order_data = {
            "user_id": user_id,
            "order_date": date.today().isoformat(),
            "payment_link": None,
            "pending": True,
            "active": True,
            "total_amount": total_amount
        }
        
        order_response = supabase.table("orders").insert(order_data).execute()
        
        if not order_response.data:
            raise HTTPException(status_code=500, detail="Erro ao criar pedido")
        
        order_id = order_response.data[0]["id"]
        print(f"[DEBUG] Pedido criado com ID: {order_id}")
        
        # Criar order_products
        order_products_data = []
        for cart_item in cart_products:
            product_price = cart_item["products"]["valor"]
            print(f"[DEBUG] Produto {cart_item['product_id']}: preço={product_price}")
            order_products_data.append({
                "order_id": order_id,
                "product_id": cart_item["product_id"],
                "quantity": cart_item["quantity"],
                "price_at_time": product_price  # Adicionar preço no momento da compra
            })
        
        print(f"[DEBUG] Dados dos produtos do pedido: {order_products_data}")
        
        # Inserir order_products
        order_products_response = supabase.table("order_products").insert(order_products_data).execute()
        
        if not order_products_response.data:
            raise HTTPException(status_code=500, detail="Erro ao criar produtos do pedido")
        
        # Criar link de pagamento no MercadoPago
        payment_link = None
        try:
            # Preparar itens para o MercadoPago
            items = []
            for cart_item in cart_products:
                product = cart_item["products"]
                items.append({
                    "title": f"{product['name']} - {product['artist']}",
                    "quantity": cart_item["quantity"],
                    "currency_id": "BRL",
                    "unit_price": float(product["valor"])
                })
            
            # Dados do pagamento
            payment_data = {
                "items": items,
                "payer": {
                    "email": current_user.get("email", "usuario@email.com")
                },
                "external_reference": str(order_id),
                "back_url": {
                    "success": "https://rocksymphony-3f7b8e8b3afd.herokuapp.com/meus-pedidos" if "herokuapp" in os.environ.get("HTTP_HOST", "") else "http://localhost:5173/meus-pedidos",
                    "failure": "https://rocksymphony-3f7b8e8b3afd.herokuapp.com/meus-pedidos" if "herokuapp" in os.environ.get("HTTP_HOST", "") else "http://localhost:5173/meus-pedidos",
                    "pending": "https://rocksymphony-3f7b8e8b3afd.herokuapp.com/meus-pedidos" if "herokuapp" in os.environ.get("HTTP_HOST", "") else "http://localhost:5173/meus-pedidos"
                }
            }
            
            # Criar preferência no MercadoPago
            result = mp.preference().create(payment_data)
            
            if "init_point" in result["response"]:
                payment_link = result["response"]["init_point"]
                print(f"[DEBUG] Link de pagamento criado: {payment_link}")
                
                # Atualizar pedido com o link de pagamento
                supabase.table("orders").update({
                    "payment_link": payment_link
                }).eq("id", order_id).execute()
            else:
                print(f"[DEBUG] Erro ao criar link de pagamento: {result}")
                
        except Exception as payment_error:
            print(f"[DEBUG] Erro ao criar pagamento MercadoPago: {str(payment_error)}")
            # Não falha o pedido se o pagamento não funcionar
        
        # Limpar carrinho - deletar produtos do carrinho usando cart_id
        delete_response = supabase.table("shoppingcart_products").delete().eq("shoppingcart_id", cart_id).execute()
        print(f"[DEBUG] Carrinho limpo")
        
        return {
            "message": "Pedido criado com sucesso!",
            "order_id": order_id,
            "total_amount": total_amount,
            "payment_link": payment_link
        }
        
    except Exception as e:
        print(f"[DEBUG] Erro ao criar pedido: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar pedido: {str(e)}")

@app.get("/api/my_orders")
async def get_my_orders(
    current_user: dict = Depends(get_current_user)
):
    """Obter pedidos do usuário logado"""
    try:
        user_id = current_user["id"]
        print(f"[DEBUG] Buscando pedidos para usuário: {user_id}")
        
        # Buscar pedidos do usuário
        orders_response = supabase.table("orders").select("*").eq("user_id", user_id).order("order_date", desc=True).execute()
        
        if not orders_response.data:
            return []
        
        orders = orders_response.data
        print(f"[DEBUG] Pedidos encontrados: {len(orders)}")
        
        # Para cada pedido, buscar os produtos
        result = []
        for order in orders:
            order_products_response = supabase.table("order_products").select("*, products(*)").eq("order_id", order["id"]).execute()
            
            products = []
            if order_products_response.data:
                for op in order_products_response.data:
                    products.append({
                        "id": op["products"]["id"],
                        "name": op["products"]["name"],
                        "artist": op["products"]["artist"],
                        "valor": op["products"]["valor"],
                        "quantity": op["quantity"],
                        "image_path": op["products"]["image_path"]
                    })
            
            result.append({
                "id": order["id"],
                "order_date": order["order_date"],
                "total_amount": order["total_amount"],
                "pending": order["pending"],
                "active": order["active"],
                "payment_link": order["payment_link"],
                "products": products
            })
        
        return result
        
    except Exception as e:
        print(f"[DEBUG] Erro ao buscar pedidos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar pedidos: {str(e)}")

@app.get("/api/admin/all_orders")
async def get_all_orders_admin(
    current_user: dict = Depends(get_current_admin_user)
):
    """Obter todos os pedidos (apenas admin)"""
    try:
        print(f"[DEBUG] Admin buscando todos os pedidos")
        
        # Buscar todos os pedidos
        orders_response = supabase.table("orders").select("*, users(email)").order("order_date", desc=True).execute()
        
        if not orders_response.data:
            return []
        
        orders = orders_response.data
        print(f"[DEBUG] Total de pedidos encontrados: {len(orders)}")
        
        # Para cada pedido, buscar os produtos
        result = []
        for order in orders:
            order_products_response = supabase.table("order_products").select("*, products(*)").eq("order_id", order["id"]).execute()
            
            products = []
            if order_products_response.data:
                for op in order_products_response.data:
                    products.append({
                        "id": op["products"]["id"],
                        "name": op["products"]["name"],
                        "artist": op["products"]["artist"],
                        "valor": op["products"]["valor"],
                        "quantity": op["quantity"],
                        "image_path": op["products"]["image_path"]
                    })
            
            result.append({
                "id": order["id"],
                "order_date": order["order_date"],
                "user_email": order["users"]["email"] if order["users"] else "N/A",
                "total_amount": order["total_amount"],
                "pending": order["pending"],
                "active": order["active"],
                "payment_link": order["payment_link"],
                "products": products
            })
        
        return result
        
    except Exception as e:
        print(f"[DEBUG] Erro ao buscar todos os pedidos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar todos os pedidos: {str(e)}")
