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
import re
import unicodedata

try:
    from .whatsapp_utils import send_whatsapp_message  # Para execução como módulo (Heroku)
except ImportError:
    from whatsapp_utils import send_whatsapp_message  # Para execução direta/local
def sanitize_filename(filename):
    """Remove caracteres especiais e sanitiza o nome do arquivo"""
    # Remover acentos e normalizar Unicode
    filename = unicodedata.normalize('NFD', filename)
    filename = ''.join(char for char in filename if unicodedata.category(char) != 'Mn')
    
    # Manter apenas letras ASCII, números, espaços, hífens e underscores
    sanitized = re.sub(r'[^a-zA-Z0-9\s\-_.]', '', filename)
    
    # Substitui múltiplos espaços por um único underscore
    sanitized = re.sub(r'\s+', '_', sanitized)
    
    # Remove underscores duplos
    sanitized = re.sub(r'_{2,}', '_', sanitized)
    
    # Remove underscores do início e fim
    sanitized = sanitized.strip('_')
    
    # Limita o tamanho para evitar nomes muito longos
    return sanitized[:100] if len(sanitized) > 100 else sanitized

# Importações para desenvolvimento local e Heroku
try:
    # Tentativa para Heroku (import relativo)
    from .models import Order, OrderProduct, SessionLocal, Product, ShoppingCart, ShoppingCartProduct, User, Artist
except ImportError:
    # Fallback para desenvolvimento local (import absoluto)
    from models import Order, OrderProduct, SessionLocal, Product, ShoppingCart, ShoppingCartProduct, User, Artist

# Importações do sistema de autenticação Supabase
try:
    # Tentativa para desenvolvimento local (import absoluto)
    from auth_routes import router as auth_router
    from auth_supabase import get_current_user, get_current_admin_user, get_current_user_optional
    from supabase_client import supabase
    from shipping_calculator import ShippingCalculator
except ImportError:
    try:
        # Tentativa para Heroku (import relativo)
        from .auth_routes import router as auth_router
        from .auth_supabase import get_current_user, get_current_admin_user, get_current_user_optional
        from .supabase_client import supabase
        from .shipping_calculator import ShippingCalculator
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
        "http://rocksymphony-3f7b8e8b3afd.herokuapp.com",
        "http://www.rocksymphony.com",
        "https://www.rocksymphony.com",
        "http://www.rocksymphony.com.br",
        "https://www.rocksymphony.com.br"
    ],  # URLs do frontend (local e produção)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas de autenticação
app.include_router(auth_router)

yag = yagmail.SMTP("henriquebarreira88@gmail.com", "keij stab puyx mocw")

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
        # Buscar produtos com JOIN para incluir nome do artista
        response = supabase.table("products").select(
            "*, artists(name, origin_country)"
        ).execute()
        
        print(f"[DEBUG] Produtos encontrados no Supabase: {len(response.data) if response.data else 0}")
        
        if response.data:
            # Processar dados para incluir artist_name no nível do produto
            processed_products = []
            for product in response.data:
                # Criar cópia do produto
                processed_product = dict(product)
                
                # Adicionar artist_name se existir relacionamento
                if product.get('artists'):
                    processed_product['artist_name'] = product['artists']['name']
                    processed_product['artist_country'] = product['artists']['origin_country']
                else:
                    processed_product['artist_name'] = 'Artista não encontrado'
                    processed_product['artist_country'] = '-'
                
                # Remover o objeto artists aninhado para evitar confusão
                if 'artists' in processed_product:
                    del processed_product['artists']
                    
                processed_products.append(processed_product)
            
            print(f"[DEBUG] Primeiro produto processado: {processed_products[0]}")
            return processed_products
        else:
            print("[DEBUG] Nenhum produto encontrado no Supabase")
            return []  # Retornar lista vazia ao invés de erro para usuários não logados
            
    except Exception as e:
        print(f"[DEBUG] Erro ao buscar produtos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar produtos: {str(e)}")

@app.get("/api/products/search")
async def search_products(
    q: str = None,  # Query para busca por nome ou artista
    country: str = None,  # Filtro por país
    stamp: str = None,  # Filtro por selo
    release_year: int = None,  # Filtro por ano
    current_user: dict = Depends(get_current_user_optional)
):
    """Buscar e filtrar produtos"""
    user_id = current_user['id'] if current_user else "anônimo"
    print(f"[DEBUG] Buscando produtos com filtros para usuário: {user_id}")
    print(f"[DEBUG] Filtros: q={q}, country={country}, stamp={stamp}, release_year={release_year}")
    
    try:
        # Construir query base com JOIN para artistas
        query = supabase.table("products").select(
            "*, artists(name, origin_country)"
        )
        
        # Aplicar filtros diretos
        if stamp:
            query = query.eq("stamp", stamp)
        if release_year:
            query = query.eq("release_year", release_year)
        
        # Executar query
        response = query.execute()
        
        products = response.data if response.data else []
        print(f"[DEBUG] Produtos encontrados antes da busca: {len(products)}")
        
        # Processar produtos e aplicar filtros
        processed_products = []
        for product in products:
            # Criar cópia do produto
            processed_product = dict(product)
            
            # Adicionar artist_name se existir relacionamento
            if product.get('artists'):
                processed_product['artist_name'] = product['artists']['name']
                processed_product['artist_country'] = product['artists']['origin_country']
                artist_name = product['artists']['name']
                artist_country = product['artists']['origin_country']
            else:
                processed_product['artist_name'] = 'Artista não encontrado'
                processed_product['artist_country'] = '-'
                artist_name = 'Artista não encontrado'
                artist_country = '-'
            
            # Filtro por país do artista
            if country and artist_country.lower() != country.lower():
                continue
            
            # Aplicar busca por texto (nome do produto ou artista)
            if q:
                search_text = q.lower()
                product_name = product.get('name', '').lower()
                if search_text not in product_name and search_text not in artist_name.lower():
                    continue
            
            # Remover o objeto artists aninhado
            if 'artists' in processed_product:
                del processed_product['artists']
            processed_products.append(processed_product)
        
        print(f"[DEBUG] Produtos retornados após filtros: {len(processed_products)}")
        return processed_products
        
    except Exception as e:
        print(f"[DEBUG] Erro ao buscar produtos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar produtos: {str(e)}")

@app.get("/api/products/filters")
async def get_product_filters(current_user: dict = Depends(get_current_user_optional)):
    """Obter filtros disponíveis para produtos"""
    try:
        # Buscar produtos para extrair filtros únicos
        response = supabase.table("products").select("stamp, release_year").execute()
        
        products = response.data if response.data else []
        
        # Extrair valores únicos
        stamps = list(set([p['stamp'] for p in products if p.get('stamp')]))
        release_years = list(set([p['release_year'] for p in products if p.get('release_year')]))
        
        # Ordenar
        stamps.sort()
        release_years.sort(reverse=True)  # Anos mais recentes primeiro
        
        return {
            "stamps": stamps,
            "release_years": release_years
        }
        
    except Exception as e:
        print(f"[DEBUG] Erro ao buscar filtros: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar filtros: {str(e)}")

class ProductCreate(BaseModel):
    name: str
    artist_id: int  # Mudança: agora referencia o ID do artista
    description: str
    valor: float
    remaining: int
    reference_code: str = ""
    stamp: str = ""
    release_year: int = None
    country: str = ""

# Schemas para Artist
class ArtistCreate(BaseModel):
    name: str
    origin_country: str
    members: str = ""
    formed_year: int = None
    description: str = ""
    genre: str = ""

class ArtistUpdate(BaseModel):
    name: str = None
    origin_country: str = None
    members: str = None
    formed_year: int = None
    description: str = None
    genre: str = None

@app.post("/api/products")
async def create_new_product(
    name: str = Form(...),
    artist_id: int = Form(0),
    description: str = Form(...),
    valor: float = Form(...),
    remaining: int = Form(...),
    reference_code: str = Form(""),
    stamp: str = Form(""),
    release_year: int = Form(None),
    country: str = Form(""),
    genre: str = Form(""),
    file: UploadFile = File(None),
    current_user: dict = Depends(get_current_user)  # Mudei para get_current_user temporariamente
):
    """Criar um novo produto (apenas admin)"""
    try:
        print(f"[DEBUG] Criando produto: {name} - artist_id: {artist_id}")
        print(f"[DEBUG] Usuário: {current_user['id']} (admin: {current_user.get('is_admin')})")
        
        # Verificar se é admin
        if not current_user.get('is_admin'):
            print(f"[DEBUG] Usuário não é admin: {current_user}")
            raise HTTPException(status_code=403, detail="Apenas administradores podem criar produtos")
        
        image_path = None
        if file and file.filename:
            print(f"[DEBUG] Processando arquivo: {file.filename}")
            print(f"[DEBUG] file.content_type: {getattr(file, 'content_type', None)}")
            print(f"[DEBUG] file.spool_max_size: {getattr(file, 'spool_max_size', None)}")
            try:
                # Ler o conteúdo do arquivo
                file_content = await file.read()
                print(f"[DEBUG] Tamanho do arquivo lido: {len(file_content) if file_content else 0}")
                file_extension = file.filename.split(".")[-1].lower() if "." in file.filename else "jpg"
                file_name = f"{sanitize_filename(name)}_{int(datetime.now().timestamp())}.{file_extension}"
                print(f"[DEBUG] Nome do arquivo para upload: {file_name}")
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
                print(f"[DEBUG] Public URL retornada: {public_url}")
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
        # Se for camisa (genre=clothe), artist_id deve ser None
        artist_id_to_save = None if (genre and genre == 'clothe') else artist_id
        new_product = {
            "name": name,
            "artist_id": artist_id_to_save,
            "description": description,
            "valor": float(valor),
            "remaining": remaining,
            "image_path": image_path,
            "reference_code": reference_code,
            "stamp": stamp,
            "release_year": release_year,
            "country": country,
            "genre": genre
        }
        
        print(f"[DEBUG] Dados do produto: {new_product}")
        
        try:
            response = supabase.table("products").insert(new_product).execute()
            print(f"[DEBUG] Resposta do Supabase: {response}")
            if hasattr(response, 'data') and response.data:
                print(f"[DEBUG] Produto criado com sucesso: {response.data[0]}")
                return {"message": f"Produto '{name}' criado com sucesso!", "product": response.data[0]}
            else:
                print(f"[DEBUG] Erro: response.data está vazio ou não existe")
                print(f"[DEBUG] response: {response}")
                raise HTTPException(status_code=500, detail="Erro ao criar produto no banco")
        except Exception as e:
            print(f"[DEBUG] Exceção ao inserir produto no Supabase: {str(e)}")
            import traceback
            traceback.print_exc()
            if hasattr(e, 'message'):
                print(f"[DEBUG] Detalhe do erro: {e.message}")
            raise HTTPException(status_code=500, detail=f"Erro ao criar produto (Supabase): {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[DEBUG] Erro ao criar produto: {str(e)}")
        print(f"[DEBUG] Tipo do erro: {type(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar produto: {str(e)}")

class ProductUpdate(BaseModel):
    name: str
    artist_id: int
    description: str
    valor: float
    remaining: int
    reference_code: str = ""
    stamp: str = ""
    release_year: int = Form(None)
    country: str = ""

@app.put("/api/products/{product_id}")
async def edit_product(
    product_id: int,
    name: str = Form(...),
    artist_id: int = Form(0),
    description: str = Form(...),
    valor: float = Form(...),
    remaining: int = Form(...),
    reference_code: str = Form(""),
    stamp: str = Form(""),
    release_year: int = Form(None),
    country: str = Form(""),
    genre: str = Form(""),
    file: UploadFile = File(None),  # Imagem opcional
    current_user: dict = Depends(get_current_admin_user)
):
    """Editar um produto existente (apenas admin)"""
    try:
        print(f"[DEBUG] Editando produto ID: {product_id}")
        print(f"[DEBUG] Dados recebidos: name={name}, artist_id={artist_id}, valor={valor}, remaining={remaining}")
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
            sanitized_name = sanitize_filename(name)
            unique_filename = f"{sanitized_name}_{int(time.time())}.{file_extension}"
            
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
        
        # Se for camisa (genre=clothe), artist_id deve ser None
        artist_id_to_save = None if (genre and genre == 'clothe') else artist_id
        update_data = {
            "name": name,
            "artist_id": artist_id_to_save,
            "description": description,
            "valor": valor,
            "remaining": remaining,
            "image_path": new_image_path,
            "reference_code": reference_code,
            "stamp": stamp,
            "release_year": release_year,
            "country": country,
            "genre": genre
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
        
        # Verificar se existem pedidos associados a este produto
        print(f"[DEBUG] Verificando pedidos associados ao produto...")
        orders_response = supabase.table("order_products").select("*").eq("product_id", product_id).execute()
        
        if orders_response.data:
            print(f"[DEBUG] Encontrados {len(orders_response.data)} pedido(s) associado(s) ao produto")
            raise HTTPException(
                status_code=400, 
                detail=f"Não é possível excluir o produto '{product_name}'. Existem {len(orders_response.data)} pedido(s) associado(s) a este produto. Para manter a integridade dos dados históricos, produtos que já foram vendidos não podem ser removidos do sistema."
            )
        
        print(f"[DEBUG] Nenhum pedido encontrado, prosseguindo com a exclusão...")
        
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

@app.get("/api/products/{product_id}/can-delete")
async def check_product_can_delete(
    product_id: int, 
    current_user: dict = Depends(get_current_user)
):
    """Verificar se um produto pode ser deletado (apenas admin)"""
    try:
        print(f"[DEBUG] Verificando se produto {product_id} pode ser deletado")
        print(f"[DEBUG] Usuário: {current_user['id']} (admin: {current_user.get('is_admin')})")
        
        # Verificar se é admin
        if not current_user.get('is_admin'):
            print(f"[DEBUG] Usuário não é admin")
            raise HTTPException(status_code=403, detail="Apenas administradores podem verificar produtos")
        
        # Buscar produto
        product_response = supabase.table("products").select("id, name").eq("id", product_id).execute()
        
        if not product_response.data:
            print(f"[DEBUG] Produto não encontrado")
            raise HTTPException(status_code=404, detail="Produto não encontrado")
        
        product = product_response.data[0]
        product_name = product["name"]
        
        # Verificar se existem pedidos associados
        orders_response = supabase.table("order_products").select("*").eq("product_id", product_id).execute()
        
        can_delete = not bool(orders_response.data)
        orders_count = len(orders_response.data) if orders_response.data else 0
        
        return {
            "can_delete": can_delete,
            "product_name": product_name,
            "orders_count": orders_count,
            "message": "Produto pode ser excluído" if can_delete else f"Não é possível excluir este produto. Existem {orders_count} pedido(s) associado(s)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[DEBUG] Erro ao verificar produto: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao verificar produto: {str(e)}")

# ===== ENDPOINTS DE ARTISTAS =====

@app.get("/api/artists")
async def get_artists(current_user: dict = Depends(get_current_user_optional)):
    """Buscar todos os artistas"""
    try:
        print("[DEBUG] Buscando artistas...")
        response = supabase.table("artists").select("*").order("name").execute()
        
        print(f"[DEBUG] Artistas encontrados: {len(response.data)}")
        return {"artists": response.data}
    
    except Exception as e:
        print(f"[DEBUG] Erro ao buscar artistas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar artistas: {str(e)}")

@app.get("/api/artists/by-country/{country}")
async def get_artists_by_country(country: str, current_user: dict = Depends(get_current_user_optional)):
    """Buscar artistas por país"""
    try:
        print(f"[DEBUG] Buscando artistas do país: {country}")
        response = supabase.table("artists").select("*").eq("origin_country", country).execute()
        
        print(f"[DEBUG] Artistas encontrados: {len(response.data)}")
        return {"artists": response.data}
    
    except Exception as e:
        print(f"[DEBUG] Erro ao buscar artistas por país: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar artistas: {str(e)}")

@app.post("/api/artists")
async def create_artist(
    name: str = Form(...),
    origin_country: str = Form(...),
    members: str = Form(""),
    formed_year: int = Form(None),
    description: str = Form(""),
    genre: str = Form(""),
    current_user: dict = Depends(get_current_user)
):
    """Criar novo artista (apenas admin)"""
    try:
        print(f"[DEBUG] Criando artista: {name}")
        
        # Verificar se é admin
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Apenas administradores podem criar artistas")
        
        new_artist = {
            "name": name,
            "origin_country": origin_country,
            "members": members,
            "formed_year": formed_year,
            "description": description,
            "genre": genre
        }
        
        print(f"[DEBUG] Dados do artista: {new_artist}")
        
        response = supabase.table("artists").insert(new_artist).execute()
        
        if response.data:
            return {"message": f"Artista '{name}' criado com sucesso!", "artist": response.data[0]}
        else:
            raise HTTPException(status_code=400, detail="Erro ao criar artista")
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[DEBUG] Erro ao criar artista: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar artista: {str(e)}")

@app.put("/api/artists/{artist_id}")
async def update_artist(
    artist_id: int,
    name: str = Form(...),
    origin_country: str = Form(...),
    members: str = Form(""),
    formed_year: int = Form(None),
    description: str = Form(""),
    genre: str = Form(""),
    current_user: dict = Depends(get_current_user)
):
    """Atualizar artista (apenas admin)"""
    try:
        print(f"[DEBUG] Atualizando artista {artist_id}")
        
        # Verificar se é admin
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Apenas administradores podem editar artistas")
        
        updated_artist = {
            "name": name,
            "origin_country": origin_country,
            "members": members,
            "formed_year": formed_year,
            "description": description,
            "genre": genre,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        response = supabase.table("artists").update(updated_artist).eq("id", artist_id).execute()
        
        if response.data:
            return {"message": f"Artista '{name}' atualizado com sucesso!"}
        else:
            raise HTTPException(status_code=404, detail="Artista não encontrado")
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[DEBUG] Erro ao atualizar artista: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar artista: {str(e)}")

@app.delete("/api/artists/{artist_id}")
async def delete_artist(
    artist_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Deletar artista (apenas admin)"""
    try:
        print(f"[DEBUG] Deletando artista {artist_id}")
        
        # Verificar se é admin
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Apenas administradores podem deletar artistas")
        
        # Buscar artista antes de deletar
        artist_response = supabase.table("artists").select("*").eq("id", artist_id).execute()
        
        if not artist_response.data:
            raise HTTPException(status_code=404, detail="Artista não encontrado")
        
        artist = artist_response.data[0]
        artist_name = artist["name"]
        
        # Verificar se existem produtos vinculados ao artista
        products_response = supabase.table("products").select("id, name").eq("artist_id", artist_id).execute()
        
        if products_response.data:
            # Verificar se algum destes produtos tem pedidos associados
            product_ids = [product["id"] for product in products_response.data]
            
            # Buscar se existem pedidos para estes produtos
            order_products_response = supabase.table("order_products").select("product_id").in_("product_id", product_ids).execute()
            
            if order_products_response.data:
                # Contar quantos produtos têm pedidos
                products_with_orders = set(op["product_id"] for op in order_products_response.data)
                total_orders = len(order_products_response.data)
                
                raise HTTPException(
                    status_code=400, 
                    detail=f"Não é possível excluir o artista '{artist_name}'. "
                           f"Existem {len(products_with_orders)} produto(s) deste artista com {total_orders} pedido(s) associado(s). "
                           f"Para manter a integridade dos dados históricos, artistas com produtos já vendidos não podem ser removidos do sistema."
                )
            
            # Se não há pedidos, mas há produtos, avisar sobre os produtos
            raise HTTPException(
                status_code=400, 
                detail=f"Não é possível excluir o artista '{artist_name}' pois existem {len(products_response.data)} produto(s) vinculado(s). "
                       f"Exclua primeiro todos os produtos deste artista."
            )
        
        # Deletar artista (não há produtos vinculados)
        response = supabase.table("artists").delete().eq("id", artist_id).execute()
        
        return {"message": f"Artista '{artist_name}' excluído com sucesso!"}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[DEBUG] Erro ao deletar artista: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao deletar artista: {str(e)}")
        raise
    except Exception as e:
        print(f"[DEBUG] Erro ao deletar artista: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao deletar artista: {str(e)}")

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

@app.post("/api/calculate-shipping")
async def calculate_shipping(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Calcular valor do frete baseado no CEP de destino"""
    try:
        destination_cep = data.get("cep")
        if not destination_cep:
            raise HTTPException(status_code=400, detail="CEP de destino é obrigatório")
        
        # Calcular peso total baseado nos produtos do carrinho
        user_id = current_user["id"]
        cart_response = supabase.table("shoppingcarts").select("*").eq("user_id", user_id).execute()
        
        if not cart_response.data:
            raise HTTPException(status_code=404, detail="Carrinho não encontrado")
        
        cart_id = cart_response.data[0]["id"]
        cart_products_response = supabase.table("shoppingcart_products").select(
            "quantity"
        ).eq("shoppingcart_id", cart_id).execute()
        
        # Peso aproximado por CD: 0.1kg, peso mínimo: 0.5kg
        total_items = sum(item["quantity"] for item in cart_products_response.data) if cart_products_response.data else 0
        total_weight = max(0.5, total_items * 0.1)
        
        # Calcular frete
        shipping_cost = ShippingCalculator.calculate_shipping(destination_cep, total_weight)
        delivery_days = ShippingCalculator.get_estimated_delivery_days(destination_cep)
        
        if shipping_cost is None:
            raise HTTPException(status_code=400, detail="Não foi possível calcular o frete para este CEP")
        
        return {
            "shipping_cost": shipping_cost,
            "delivery_days": delivery_days,
            "weight_kg": total_weight,
            "origin_cep": ShippingCalculator.ORIGIN_CEP
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular frete: {str(e)}")

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
            "*, product:products(*, artists(name))"
        ).eq("shoppingcart_id", cart_id).execute()
        
        print(f'Produtos encontrados: {len(cart_products.data)}')
        
        # Formatar resposta
        formatted_products = []
        for item in cart_products.data:
            product = item["product"]
            
            # Buscar nome do artista
            artist_name = "Artista não informado"
            if product.get("artists"):
                artist_name = product["artists"]["name"]
            
            formatted_product = {
                "id": product["id"],
                "name": product["name"],
                "artist": artist_name,
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

        address_data = address_response.data[0]

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
            "*, product:products(*, artists(name))"
        ).eq("shoppingcart_id", cart_id).execute()

        if not cart_products_response.data:
            raise HTTPException(status_code=400, detail="Carrinho está vazio")

        print(f"Produtos no carrinho: {len(cart_products_response.data)}")

        # Calcular peso total para o frete
        total_items = sum(item["quantity"] for item in cart_products_response.data)
        total_weight = max(0.5, total_items * 0.1)  # 0.1kg por CD, mínimo 0.5kg
        
        # Calcular frete
        shipping_cost = ShippingCalculator.calculate_shipping(address_data["cep"], total_weight)
        if shipping_cost is None:
            shipping_cost = 35.00  # Valor padrão em caso de erro
        
        print(f"Frete calculado: R$ {shipping_cost}")

        # Calcular total dos produtos
        total_value = 0
        for cart_item in cart_products_response.data:
            product = cart_item["product"]
            quantity = cart_item["quantity"]
            total_value += float(product["valor"]) * quantity

        print(f"Total calculado: {total_value}")
        
        # Total final incluindo frete
        total_with_shipping = total_value + shipping_cost
        print(f"Total com frete: {total_with_shipping}")

        # Criar o pedido no Supabase
        print("Criando pedido...")
        order_data_db = {
            "user_id": user_id,
            "address_id": address_id,
            "total_amount": total_with_shipping,
            "shipping_cost": shipping_cost,
            "pending": True,
            "active": True
        }
        order_response = supabase.table("orders").insert(order_data_db).execute()
        if not order_response.data:
            raise HTTPException(status_code=500, detail="Erro ao criar pedido")
        new_order_id = order_response.data[0]["id"]
        print(f"Pedido criado: {new_order_id}")

        # Enviar mensagem WhatsApp para o admin
        try:
            # Configuração do WhatsApp Business API (Meta/Facebook)
            admin_phone = "5521976432296"  # Número de teste cadastrado no painel, formato E.164 (sem espaços, só números)
            phone_number_id = "733815513144780"  # ID do número de telefone do painel
            access_token = "EAARrlZAiZB0h4BPFOZA30m0qpeXl6QYL696O9dqCr5cUkd6Hav9zvBYnZBpTn7wQyzpvdtc4yghl3GBeK4UuzwcCn7qaZCmkYky7idPLdiDEkjZAdoybXQEBnYHvrMthmR4ZALZCtgEs10NVGtZB0K2uZBYTHSDkB7VzKpd0MwZABicb0s9IyhfjT0ouOaQQzmScGzj0YTpZCoW2a7HrpmxpgyJWuRi3cStpIyhH9jO6Ec0ft62ln9je"
            # Para números de teste, só é permitido enviar template aprovado (ex: hello_world)
            send_whatsapp_message(admin_phone, "", phone_number_id, access_token, use_template=True, template_name="hello_world", template_lang="en_US")
        except Exception as e:
            print(f"[WHATSAPP] Falha ao notificar admin: {e}")

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

        # Criar link de pagamento no MercadoPago
        payment_link = None
        try:
            # Preparar itens para o MercadoPago
            items = []
            for cart_item in cart_products_response.data:
                product = cart_item["product"]
                
                # Buscar nome do artista
                artist_name = "Artista não informado"
                if product.get("artists"):
                    artist_name = product["artists"]["name"]
                
                items.append({
                    "title": f"{product['name']} - {artist_name}",
                    "quantity": cart_item["quantity"],
                    "currency_id": "BRL",
                    "unit_price": float(product["valor"])
                })
            
            # Adicionar frete como item separado
            if shipping_cost > 0:
                items.append({
                    "title": "Frete",
                    "quantity": 1,
                    "currency_id": "BRL", 
                    "unit_price": float(shipping_cost)
                })
            
            # Dados do pagamento
            payment_data = {
                "items": items,
                "payer": {
                    "email": current_user.get("email", "usuario@email.com")
                },
                "external_reference": str(new_order_id),
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
                print(f"Link de pagamento criado: {payment_link}")
                
                # Atualizar pedido com o link de pagamento
                supabase.table("orders").update({
                    "payment_link": payment_link
                }).eq("id", new_order_id).execute()
            else:
                print(f"Erro ao criar link de pagamento: {result}")
                
        except Exception as payment_error:
            print(f"Erro ao criar pagamento MercadoPago: {str(payment_error)}")
            # Não falha o pedido se o pagamento não funcionar

        # Limpar carrinho
        print("Limpando carrinho...")
        supabase.table("shoppingcart_products").delete().eq("shoppingcart_id", cart_id).execute()
        
        print("Pedido criado com sucesso!")
        yag.send(
            to="leonahoum@gmail.com",
            subject="Pedido Feito!",
            contents="Foi registrado um novo pedido!"
        )
        return {
            "message": "Pedido criado com sucesso",
            "order_id": new_order_id,
            "total_amount": total_with_shipping,
            "products_total": total_value,
            "shipping_cost": shipping_cost,
            "payment_link": payment_link,
            "redirect_to": "/meus-pedidos" if payment_link else "/minhas-reservas",
            "order_details": {
                "id": new_order_id,
                "user_id": user_id,
                "address_id": address_id,
                "total_amount": total_with_shipping,
                "shipping_cost": shipping_cost,
                "payment_link": payment_link,
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
            "*, order_products(*, product:products(*, artists(name)))"
        ).eq("user_id", user_id).execute()
        
        result = []
        for order in orders_response.data:
            products = []
            total_value = 0
            
            for order_product in order.get("order_products", []):
                product = order_product["product"]
                quantity = order_product["quantity"]
                price_at_time = float(order_product.get("price_at_time", product["valor"]))
                
                # Buscar nome do artista
                artist_name = "Artista não informado"
                if product.get("artists"):
                    artist_name = product["artists"]["name"]
                
                print(f"[DEBUG] Produto no pedido {order['id']}: {product.get('name', 'N/A')}")
                print(f"  image_path: {product.get('image_path', 'N/A')}")
                print(f"  artist: {artist_name}")
                
                products.append({
                    "id": product["id"],  # Adicionar ID do produto
                    "name": product["name"],
                    "artist": artist_name,
                    "quantity": quantity,
                    "valor": price_at_time,
                    "image_path": product.get("image_path")  # Adicionar image_path
                })
                total_value += price_at_time * quantity
            
            result.append({
                "id": order["id"],
                "order_date": order["order_date"],
                "pending": order["pending"],
                "sent": order.get("sent", False),  # Adicionar campo sent
                "active": order["active"],
                "payment_link": order.get("payment_link"),  # Adicionar payment_link
                "total_amount": order.get("total_amount", total_value),  # Usar total_amount do banco ou calculado
                "shipping_cost": order.get("shipping_cost", 0),  # Adicionar valor do frete
                "tracking_code": order.get("tracking_code"),  # Adicionar código de rastreamento
                "products": products
            })
        
        return result
        
    except Exception as e:
        print(f"Erro ao buscar pedidos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar pedidos: {str(e)}")
    

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
    current_user: dict = Depends(get_current_admin_user)
):
    """Obter todos os pedidos (apenas admin)"""
    try:
        # Buscar todos os pedidos com informações do usuário
        orders_response = supabase.table("orders").select(
            "*, users(usuario), order_products(*, products(*, artists(name)))"
        ).execute()
        
        result = []
        for order in orders_response.data:
            products = []
            total_value = 0
            
            for order_product in order.get("order_products", []):
                product = order_product["product"]
                quantity = order_product["quantity"]
                price_at_time = float(order_product.get("price_at_time", product["valor"]))
                
                # Buscar nome do artista
                artist_name = "Artista não informado"
                if product.get("artists"):
                    artist_name = product["artists"]["name"]
                
                products.append({
                    "id": product["id"],
                    "name": product["name"],
                    "artist": artist_name,
                    "quantity": quantity,
                    "valor": price_at_time,
                    "image_path": product.get("image_path")
                })
                total_value += price_at_time * quantity
            
            result.append({
                "id": order["id"],
                "order_date": order["order_date"],
                "pending": order["pending"],
                "sent": order.get("sent", False),
                "active": order["active"],
                "user_name": order["users"]["usuario"] if order["users"] else "Usuário sem nome",
                "total_amount": order.get("total_amount", total_value),
                "products": products
            })
        
        # Ordenar por data mais recente primeiro
        result.sort(key=lambda x: x["order_date"], reverse=True)
        return result
        
    except Exception as e:
        print(f"Erro ao buscar todos os pedidos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar pedidos: {str(e)}")

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

@app.get("/api/admin/all_orders")
async def get_all_orders_admin(
    current_user: dict = Depends(get_current_admin_user)
):
    """Obter todos os pedidos (apenas admin)"""
    try:
        print(f"[DEBUG] Admin buscando todos os pedidos")
        
        # Buscar todos os pedidos com endereços
        orders_response = supabase.table("orders").select("*, users(email), addresses(*)").order("order_date", desc=True).execute()
        
        if not orders_response.data:
            return []
        
        orders = orders_response.data
        print(f"[DEBUG] Total de pedidos encontrados: {len(orders)}")
        
        # Para cada pedido, buscar os produtos
        result = []
        for order in orders:
            order_products_response = supabase.table("order_products").select("*, products(*, artists(name))").eq("order_id", order["id"]).execute()
            
            products = []
            if order_products_response.data:
                for op in order_products_response.data:
                    # Buscar nome do artista
                    artist_name = "Artista não informado"
                    if op["products"]["artists"]:
                        artist_name = op["products"]["artists"]["name"]
                    
                    products.append({
                        "id": op["products"]["id"],
                        "name": op["products"]["name"],
                        "artist": artist_name,
                        "valor": op["products"]["valor"],
                        "quantity": op["quantity"],
                        "image_path": op["products"]["image_path"]
                    })
            
            # Calcular subtotal dos produtos
            subtotal = sum(float(p["valor"]) * p["quantity"] for p in products)
            shipping_cost = float(order.get("shipping_cost", 0))
            
            result.append({
                "id": order["id"],
                "order_date": order["order_date"],
                "user_email": order["users"]["email"] if order["users"] else "N/A",
                "total_amount": order["total_amount"],
                "subtotal": subtotal,
                "shipping_cost": shipping_cost,
                "pending": order["pending"],
                "sent": order.get("sent", False),
                "active": order["active"],
                "payment_link": order["payment_link"],
                "tracking_code": order.get("tracking_code"),
                "delivery_address": order.get("addresses"),  # Endereço de entrega
                "products": products
            })
        
        return result
        
    except Exception as e:
        print(f"[DEBUG] Erro ao buscar todos os pedidos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar todos os pedidos: {str(e)}")

@app.put("/api/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    request: Request,
    pending: bool = None,
    sent: bool = None,
    current_user: dict = Depends(get_current_admin_user)
):
    """Atualizar status de um pedido (apenas admin)"""
    try:
        print(f"[DEBUG] Atualizando status do pedido {order_id}")
        print(f"[DEBUG] pending: {pending}, sent: {sent}")
        
        # Construir dados para atualização
        update_data = {}
        if pending is not None:
            update_data["pending"] = pending
        if sent is not None:
            update_data["sent"] = sent
            
        # Verificar se há dados no body da requisição (tracking_code)
        try:
            body = await request.json()
            if "tracking_code" in body and body["tracking_code"]:
                update_data["tracking_code"] = body["tracking_code"]
                print(f"[DEBUG] Código de rastreamento: {body['tracking_code']}")
        except Exception as e:
            print(f"[DEBUG] Nenhum body JSON ou erro ao processar: {e}")
            
        if not update_data:
            raise HTTPException(status_code=400, detail="Nenhum status fornecido para atualização")
        
        # Atualizar o pedido
        response = supabase.table("orders").update(update_data).eq("id", order_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Pedido não encontrado")
        
        return {"message": "Status do pedido atualizado com sucesso", "order": response.data[0]}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao atualizar status do pedido: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar status do pedido: {str(e)}")

@app.post("/api/webhook/mercadopago")
async def mercadopago_webhook(request: Request):
    """Webhook para notificações do MercadoPago"""
    try:
        body = await request.body()
        print(f"[DEBUG] Webhook MercadoPago recebido: {body}")
        
        # Parsear dados do webhook
        data = await request.json()
        
        if data.get("type") == "payment":
            payment_id = data.get("data", {}).get("id")
            
            if payment_id:
                # Buscar detalhes do pagamento
                payment_info = mp.payment().get(payment_id)
                
                if payment_info["status"] == 200:
                    payment_data = payment_info["response"]
                    external_reference = payment_data.get("external_reference")
                    status = payment_data.get("status")
                    
                    print(f"[DEBUG] Pagamento {payment_id} - Status: {status} - Pedido: {external_reference}")
                    
                    if external_reference and status == "approved":
                        # Atualizar pedido como pago
                        supabase.table("orders").update({
                            "pending": False,
                            "active": True
                        }).eq("id", external_reference).execute()
                        
                        print(f"[DEBUG] Pedido {external_reference} marcado como pago")
                        # Enviar mensagem WhatsApp ao admin sobre pagamento aprovado
                        try:
                            from whatsapp_utils import send_whatsapp_message
                            admin_phone = "SEU_NUMERO_AQUI"  # Ex: "5511999999999"
                            api_url = "SUA_API_URL_AQUI"     # Ex: "https://api.ultramsg.com/instanceXXXX/messages/chat"
                            api_token = "SEU_TOKEN_AQUI"
                            msg = f"Pagamento aprovado do pedido #{external_reference}!"
                            send_whatsapp_message(admin_phone, msg, api_url, api_token)
                        except Exception as e:
                            print(f"[WHATSAPP] Falha ao notificar admin (pagamento): {e}")
        yag.send(
            to="leonahoum@gmail.com",
            subject="Pedido Pago!",
            contents="Foi registrado um pagamento de pedido!"
        )
        return {"status": "ok"}
        
    except Exception as e:
        print(f"[DEBUG] Erro no webhook: {str(e)}")
        return {"status": "error", "message": str(e)}



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

# ===== FINAL DO ARQUIVO =====

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)