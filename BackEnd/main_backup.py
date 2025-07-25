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
#from .models import Order, OrderProduct, SessionLocal, Product, ShoppingCart, ShoppingCartProduct, User
from models import Order, OrderProduct, SessionLocal, Product, ShoppingCart, ShoppingCartProduct, User

# Importações do sistema de autenticação Supabase
from auth_routes import router as auth_router
from auth_supabase import get_current_user, get_current_admin_user, get_current_user_optional

# Criação da instância do FastAPI
app = FastAPI(title="Rock Symphony API", version="1.0.0", description="Marketplace de CDs de Rock")

# Configuração do MercadoPago
mp = mercadopago.SDK("APP_USR-6446237437103604-040119-bca68443def1fb05bfa6643f416e2192-96235831")

# Configuração de arquivos estáticos
# app.mount("/assets", StaticFiles(directory=Path(os.getcwd()) / "FrontEnd" / "dist" / "assets"), name="assets")
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # URLs do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas de autenticação
app.include_router(auth_router)

# Função para obter a sessão do banco de dados
def get_db_session():
    db = SessionLocal()  # Cria a sessão usando a configuração do banco
    try:
        yield db  # Garante que o banco será fechado após a execução
    finally:
        db.close()  # Fecha a sessão

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
        # Tenta conectar ao banco de dados com uma consulta simples
        db = SessionLocal()
        db.execute(text("SELECT 1"))  # Usando a função `text()` para a consulta SQL
        db.close()
        
        # Se a consulta for bem-sucedida
        return {"status": "ok"}
    
    except OperationalError:
        # Se houver erro de conexão com o banco de dados
        return {"status": "error", "message": "Database connection failed"}, 500




class UserCreate(BaseModel):
    username: str
    email: str


def create_user(db: Session, username: str, email: str, namespace_id: int):
    password = generate_random_password()
    hashed_password = hash_password(password)
    user = User(username=username, email=email, hashed_password=hashed_password, is_admin=False, namespace_id=namespace_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    yag = yagmail.SMTP(user="henriquebarreira88@gmail.com", password="yrdh enwq dkdy tsnz")
    yag.send(to=user.email,
        subject="Bem-vindo à plataforma!",
        contents=f"Olá {username}, sua conta foi criada. Sua senha temporária é: {password}"
    )

    return user

def update_user(db: Session, user_id: str, username: str, email: str ):
    user = db.query(User).filter(User.id == user_id).first()
    user.username = username
    user.email = email
    db.commit()
    db.refresh(user)
    yag = yagmail.SMTP(user="henriquebarreira88@gmail.com", password="yrdh enwq dkdy tsnz")
    yag.send(to=user.email,
        subject="Dados atualizados com sucesso!",
        contents=f"Olá {username}, seus dados foram atualizados com sucesso."
    )

    return user



# Função para converter o usuário do Supabase para o formato esperado pelo sistema
def get_user_from_supabase(current_user: dict, db: Session):
    """Converte o usuário do Supabase para o formato esperado pelos endpoints"""
    # Buscar o usuário na tabela local pelo ID do Supabase
    user = db.query(User).filter(User.id == current_user["id"]).first()
    
    if not user:
        # Se não encontrar, criar um novo usuário com os dados do Supabase
        user = User(
            id=current_user["id"],
            usuario=current_user.get("usuario"),
            is_admin=current_user.get("is_admin", False)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user

def get_schedules(user_id: str, db: Session):
    try:
        # Buscar todas as orders ativas (não filtrar por namespace_id)
        orders = db.query(Order).join(Product).filter(Order.active == True).all()

        if not orders:
            print(f"Nenhum schedule encontrado para o user_id: {user_id}")

        result = [
            {
                'schedule_date': order.schedule_date.isoformat(),  # Converte para string ISO
                'space_id': order.space.id,
                'space_name': ', '.join([order_product.product.name for order_product in order.products]),
                # Retorna o payment_link somente para os schedules que pertencem ao usuário
                'payment_link': order.payment_link if order.user_id == user_id else None
            }
            for order in orders
        ]

        print(f"Schedules encontrados: {len(result)}")
        return result
    except Exception as e:
        print(f"Erro ao buscar schedules: {str(e)}")
        raise


@app.get("/api/schedules")
async def get_schedules_endpoint(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db_session)):
    user = get_user_from_supabase(current_user, db)
    return get_schedules(user.id, db)

@app.get("/api/products")
async def get_available_products(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db_session)):
    # Buscar todos os produtos disponíveis
    products = db.query(Product).all()
    if not products:
        raise HTTPException(status_code=404, detail="Produtos não encontrados")
    return products


class AddProductToCartRequest(BaseModel):
    productId: int
    quantity: int = 1 

@app.post("/api/add_product_to_cart")
def add_product_to_cart(newProduct: AddProductToCartRequest, db: Session = Depends(get_db_session), current_user: dict = Depends(get_current_user)):
    # Encontrar o carrinho do usuário
    user = get_user_from_supabase(current_user, db)
    
    shopping_cart = db.query(ShoppingCart).filter(ShoppingCart.user_id == user.id).first()
    
    # Se o carrinho não existir, criar um novo
    if not shopping_cart:
        shopping_cart = ShoppingCart(user_id=user.id)
        db.add(shopping_cart)
        db.commit()
        db.refresh(shopping_cart)
    
    # Adicionar o produto ao carrinho (ou atualizar a quantidade, se já existir)
    cart_product = db.query(ShoppingCartProduct).filter(
        ShoppingCartProduct.shoppingcart_id == shopping_cart.id,
        ShoppingCartProduct.product_id == newProduct.productId
    ).first()
    
    if cart_product:
        cart_product.quantity += newProduct.quantity  # Atualiza a quantidade se o produto já estiver no carrinho
    else:
        cart_product = ShoppingCartProduct(
            shoppingcart_id=shopping_cart.id,
            product_id=newProduct.productId,
            quantity=newProduct.quantity
        )
        db.add(cart_product)
    
    db.commit()
    db.refresh(cart_product)
    return cart_product


@app.get("/api/get_cart_products")
def get_cart_products(db: Session = Depends(get_db_session), current_user: dict = Depends(get_current_user)):
    # Encontrar o carrinho do usuário
    user = get_user_from_supabase(current_user, db)
    shopping_cart = db.query(ShoppingCart).filter(ShoppingCart.user_id == user.id).first()

    if not shopping_cart:
        return []

    # Buscar os produtos do carrinho e suas quantidades
    cart_items = db.query(ShoppingCartProduct, Product).join(Product).filter(ShoppingCartProduct.shoppingcart_id == shopping_cart.id).all()

    result = []
    for cart_item, product in cart_items:
        result.append({
            "id": product.id,
            "name": product.name,
            "valor": product.valor,
            "quantity": cart_item.quantity  # Retorna a quantidade
        })

    return result



@app.post("/api/handle_checkout")
def create_order(db: Session = Depends(get_db_session), current_user: dict = Depends(get_current_user)):
    # Encontrar o carrinho do usuário
    user = get_user_from_supabase(current_user, db)
    shopping_cart = db.query(ShoppingCart).filter(ShoppingCart.user_id == user.id).first()

    if not shopping_cart:
        raise HTTPException(status_code=404, detail="Carrinho não encontrado")

    # Obter os produtos do carrinho
    cart_products = db.query(ShoppingCartProduct).filter(ShoppingCartProduct.shoppingcart_id == shopping_cart.id).all()

    if not cart_products:
        raise HTTPException(status_code=400, detail="Carrinho está vazio")

    # Criar o pedido
    new_order = Order(
        order_date=date.today(),
        user_id=user.id,
        payment_link=None,  # Este é um campo que você pode atualizar depois com o link de pagamento
        pending=True,
        active=True
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # Criar a relação entre o pedido e os produtos

    total_order_value = 0
    for cart_product in cart_products:
        # Associar o produto com o pedido
        total_order_value += cart_product.product.valor * cart_product.quantity
        order_product = OrderProduct(
            order_id=new_order.id,
            product_id=cart_product.product_id,
            quantity=cart_product.quantity
        )
        db.add(order_product)
    
    # Commit para salvar os produtos do pedido
    db.commit()
    product_names = ''
    for cart_product in cart_products:
        product_names += cart_product.product.name+ ', '
    
    product_names = product_names[:-2]

    # Remover os produtos do carrinho
    db.query(ShoppingCartProduct).filter(ShoppingCartProduct.shoppingcart_id == shopping_cart.id).delete()
    db.commit()

    payment_data = {
        "items": [
            {
                "title": f"Compra dos Produtos: {product_names}",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": total_order_value  # Ajuste o valor conforme necessário
            }
        ],
        "payer": {
            "email": "usuario@email.com"  # Troque pelo email real do usuário
        },
        "external_reference": str(new_order.id),  # ID da reserva
        "back_urls": {
            "success": "http://localhost:5173/minhas-reservas",
            "failure": "http://localhost:5173/minhas-reservas",
            "pending": "http://localhost:5173/minhas-reservas"
        },
        "auto_return": "approved"
    }

# 🔹 Faz a requisição para criar o link de pagamento
    result = mp.preference().create(payment_data)

    if "init_point" not in result["response"]:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao gerar link de pagamento.")

    payment_link = result["response"]["init_point"]  # Link do MercadoPago

    # 🔹 Atualiza o Order com o link de pagamento
    new_order.payment_link = payment_link
    db.commit()

    return JSONResponse(status_code=200, content={"message": "Pedido criado com sucesso", "order_id": new_order.id})

@app.get("/api/configuracoes")
async def get_available_configs(current_user: User = Depends(get_logged_user), db: Session = Depends(get_db_session)):
    # Obter a configuração do usuário
    config = db.query(User).filter(User.id == current_user.id).first().namespace_config
    namespace_id = db.query(User).filter(User.id == current_user.id).first().namespace_id
    spaces = db.query(Product).filter(Product.namespace_id == namespace_id).all()
    days_until_next_schedule_is_available = 0
    spaces_locked_untill = {}


    if config.consider_last_schedule:
        # Pegar o agendamento mais recente do usuário
        latest_schedule = db.query(Order).filter(Order.user_id == current_user.id, Order.active == True).order_by(Order.schedule_date.desc()).first()
        
        # Calcular a quantidade de dias até o próximo agendamento estar disponível
        if latest_schedule:
            today = date.today()  # Data de hoje
            days_until_next_schedule_is_available = latest_schedule.space.min_days - (today - latest_schedule.schedule_date).days
        else:
            # Caso não exista agendamento, o valor seria 0 (ou algum outro valor padrão)
            days_until_next_schedule_is_available = 0
    else:
        days_until_next_schedule_is_available = 0
    
        today = date.today()
        for space in spaces:
            user_last_schedule_for_space = db.query(Order).filter(Order.user_id == current_user.id, Order.space_id == space.id).order_by(Order.schedule_date.desc()).first()
            if user_last_schedule_for_space:
                space_locked_untill = user_last_schedule_for_space.schedule_date + timedelta(days=space.min_days)
                spaces_locked_untill[space.name] = space_locked_untill
    return {
        "has_pagseguro": config.has_pagseguro,
        "max_payment_time": config.max_payment_time,
        "min_schedule_interval": max(config.min_schedule_interval, days_until_next_schedule_is_available),
        "consider_last_schedule": config.consider_last_schedule,
        "space_locked_untill": spaces_locked_untill
    }


@app.post("/api/usuarios")
def create_new_user(user: UserCreate, current_user: User = Depends(get_logged_user), db: Session = Depends(get_db_session)):
    namespace_id = db.query(User).filter(User.id == current_user.id).first().namespace_id

    return create_user(db, user.username, user.email, namespace_id)


class UserUpdate(BaseModel):
    username: str
    email: str


@app.put("/api/usuarios/{user_id}")
async def edit_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db_session)):
    try:
        updated_user = update_user(db, user_id, user.username, user.email)
        return {"message": f"Usuário '{updated_user.username}' atualizado com sucesso!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao editar usuário: " + str(e))
    finally:
        db.close()

class ConfigUpdate(BaseModel):
    considerarUltimoAgendamento: bool
    tempoMaximoPagamento: str
    intervaloMinimo: str
    hasPagseguro: bool

@app.put("/api/configuracoes")
async def update_configuracoes(config: ConfigUpdate, current_user: User = Depends(get_logged_user), db: Session = Depends(get_db_session)):
    # Buscar o usuário no banco de dados
    user = db.query(User).filter(User.id == current_user.id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Atualizar as configurações do namespace do usuário
    namespace_config = user.namespace_config
    
    # Atualizando os valores
    namespace_config.has_pagseguro = config.hasPagseguro
    namespace_config.max_payment_time = config.tempoMaximoPagamento
    namespace_config.min_schedule_interval = config.intervaloMinimo
    namespace_config.consider_last_schedule = config.considerarUltimoAgendamento
    
    # Commit para salvar as alterações no banco de dados
    db.commit()

    return {
        "message": "Configurações atualizadas com sucesso!",
        "new_config": {
            "has_pagseguro": namespace_config.has_pagseguro,
            "max_payment_time": namespace_config.max_payment_time,
            "min_schedule_interval": namespace_config.min_schedule_interval,
            "consider_last_schedule": namespace_config.consider_last_schedule,
        }
    }
    




class UserRequest(BaseModel):
    username: str

@app.post("/me")
async def get_current_user(
    token: str = Security(oauth2_scheme), db: Session = Depends(get_db_session)
):
    user_data = decode_token(token)  # Decodifica o token JWT e pega os dados do usuário
    if not user_data:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    user = db.query(User).filter(User.id == user_data["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return {
        "username": user.username,
        "is_admin": user.is_admin,
    }


class SpaceCreate(BaseModel):
    name: str
    valor: float
    min_days: int

# Função para criar um novo espaço
def create_space(db, name: str, artist: str, description: str, valor: float, remaining: int, image_path: str = None):
    valor = int(valor)
    new_space = Product(
        name=name,
        artist=artist,
        description=description,
        valor=valor,
        remaining=remaining,
        image_path=image_path  # nova coluna no seu model (precisa existir)
    )
    db.add(new_space)
    db.commit()
    db.refresh(new_space)
    return new_space


@app.post("/spaces")
async def create_new_space(
    name: str = Form(...),
    artist: str = Form(...),
    description: str = Form(...),
    valor: float = Form(...),
    remaining: int = Form(...),
    image: UploadFile = File(None),
    current_user: User = Depends(get_logged_user),
    db: Session = Depends(get_db_session)
):
    try:
        image_path = None
        if image:
            file_location = f"uploads/{image.filename}"
            with open(file_location, "wb") as buffer:
                buffer.write(await image.read())
            image_path = file_location

        new_space = create_space(db, name, artist, description, valor, remaining, image_path=image_path)
        return {"message": f"Espaço '{new_space.name}' criado com sucesso!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao cadastrar espaço: " + str(e))
    finally:
        db.close()

class OrderCreate(BaseModel):
    productName: str


def create_order(db: Session, productId: str, user_id):
    # Busca o produto no banco
    product = db.query(Product).filter(Product.id == productId).first()
    
    if not product:
        raise Exception(f"Product '{productId}' não encontrado.")

    # Cria o Order e salva no banco (ainda sem o pagamento)
    new_order = Order(user_id=user_id, order_date=datetime.now(), total_amount=product.valor)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # 🔹 Criando o pagamento no MercadoPago 🔹
    payment_data = {
        "items": [
            {
                "title": f"Compra do Produto {product.name}",
                "quantity": 1,
                    "currency_id": "BRL",
                    "unit_price": new_order.product.valor  # Ajuste o valor conforme necessário
                }
            ],
            "payer": {
                "email": "usuario@email.com"  # Troque pelo email real do usuário
            },
            "external_reference": str(new_order.id),  # ID da reserva
            "back_urls": {
                "success": "http://localhost:5173/minhas-reservas",
                "failure": "http://localhost:5173/minhas-reservas",
                "pending": "http://localhost:5173/minhas-reservas"
            },
            "auto_return": "approved"
        }

    # 🔹 Faz a requisição para criar o link de pagamento
    result = mp.preference().create(payment_data)

    if "init_point" not in result["response"]:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao gerar link de pagamento.")

    payment_link = result["response"]["init_point"]  # Link do MercadoPago

    # 🔹 Atualiza o Order com o link de pagamento
    new_order.payment_link = payment_link
    db.commit()

    return new_order
    
@app.post("/orders")
async def create_new_order(order: OrderCreate, current_user: User = Depends(get_logged_user), db: Session = Depends(get_db_session)):
    try:
        new_order = create_order(db, order.productName, current_user.id)
        return {
            "message": f"Pedido criado com sucesso!",
            "payment_link": new_order.payment_link
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao cadastrar espaço: " + str(e))


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def generate_random_password(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


@app.get("/api/usuarios")
async def list_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db_session), current_user: User = Depends(get_logged_user)):
    """
    Endpoint para listar usuários de forma paginada. Exclui o usuário que está fazendo a requisição.
    """
    try:
        # Consulta os usuários no banco de dados, com paginamento
        users = db.query(User).filter(User.id != current_user.id).offset(skip).limit(limit).all()

        # Verifica se encontrou algum usuário
        if not users:
            raise HTTPException(status_code=404, detail="Nenhum usuário encontrado.")

        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar usuários: {str(e)}")


@app.post("/api/importar-usuarios")
async def import_users(
    file: UploadFile = File(...),
    current_user: User = Depends(get_logged_user),
    db: Session = Depends(get_db_session),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Apenas arquivos CSV são permitidos.")

    contents = await file.read()
    decoded_content = contents.decode("utf-8").splitlines()
    csv_reader = csv.reader(decoded_content)
    next(csv_reader, None)

    created_users = []

    for row in csv_reader:
        if len(row) < 3:
            continue  # Pula linhas inválidas
        
        _, username, email = row  # Ignora a primeira coluna (data)
        existing_user = db.query(User).filter(User.email == email).first()
        
        if existing_user:
            continue  # Pula usuários já existentes

        password = generate_random_password()
        hashed_password = hash_password(password)  # Assumindo que você tenha essa função implementada
        
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            namespace_id=current_user.namespace_id
        )
        db.add(new_user)
        created_users.append((username, email, password))

    db.commit()
    yag = yagmail.SMTP(user="henriquebarreira88@gmail.com", password="yrdh enwq dkdy tsnz")

    # Enviar e-mail para cada usuário criado
    for username, email, password in created_users:
        yag.send(to=email,
                    subject="Bem-vindo à plataforma!",
                    contents=f"Olá {username}, sua conta foi criada. Sua senha temporária é: {password}"
        )
        print("Email enviado com sucesso!")

    return {"message": f"{len(created_users)} usuários foram criados e receberam suas credenciais."}

class SpaceUpdate(BaseModel):
    name: str
    valor: float
    min_days: int

# Função para editar um espaço
def update_product(db: Session, space_id: int, name: str, valor: float, min_days: str):
    product = db.query(Product).filter(Product.id == space_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Espaço não encontrado")

    product.name = name
    product.valor = valor
    product.min_days = min_days
    db.commit()
    db.refresh(product)
    return product

# Função para excluir um espaço
def delete_space(db: Session, space_id: int):
    space = db.query(Product).filter(Product.id == space_id).first()
    if not space:
        raise HTTPException(status_code=404, detail="Espaço não encontrado")

    db.delete(space)
    db.commit()
    return {"message": f"Espaço '{space.name}' excluído com sucesso!"}

# Endpoint para editar um espaço
@app.put("/spaces/{product_id}")
async def edit_space(product_id: int, product: SpaceUpdate, current_user: User = Depends(get_logged_user), db: Session = Depends(get_db_session)):
    try:
        updated_product = update_product(db, product_id, product.name, product.valor, product.min_days)
        return {"message": f"Espaço '{updated_product.name}' atualizado com sucesso!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao editar espaço: " + str(e))
    finally:
        db.close()

# Endpoint para excluir um espaço
@app.delete("/spaces/{space_id}")
async def delete_space_endpoint(space_id: int, db: Session = Depends(get_db_session)):
    try:
        result = delete_space(db, space_id)
        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao excluir espaço: " + str(e))
    finally:
        db.close()
# Rota de teste para verificar se o servidor está funcionando
        
@app.get("/api/my_schedules")
async def get_schedules_endpoint(current_user: User = Depends(get_logged_user), db: Session = Depends(get_db_session)):
    orders = db.query(Order).filter(Order.user_id == current_user.id).all()

    if not orders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma reserva encontrada para este usuário"
        )

    result = [
        {
            'schedule_date': datetime.now(),  # Converte para string ISO
            'space_id': 1,
            'space_name': ', '.join([order_product.product.name for order_product in order.products]),
            'namespace': '',
            'pending': order.pending,
            'cancelled': not order.active,
            'payment_link': order.payment_link if order.user_id == int(current_user.id) else None
        }
        for order in orders
    ]

    return result


@app.get("/api/all_schedules")
async def get_schedules_endpoint(current_user: User = Depends(get_logged_user), db: Session = Depends(get_db_session)):
    orders = db.query(Order).all()

    if not orders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma reserva encontrada para este usuário"
        )
    result = {
        'schedules': [
            {
                'id': order.id,
                'schedule_date': datetime.now(),
                'space_id': 1,
                'space_name': ', '.join([order_product.product.name for order_product in order.products]),
                'namespace': 'bla',
                'payment_link': order.payment_link,
                'pending': order.pending,
                'user_name': order.user.username,
                'cancelled': not order.active
                
            }
            for order in orders
        ],
    'is_admin': current_user.is_admin
    }

    return result

def get_preference_id(payment_link: str):
    parsed_url = urlparse(payment_link)
    query_params = parse_qs(parsed_url.query)
    return query_params.get("pref_id", [None])[0]


class CancelScheduleRequest(BaseModel):
    refund: bool = False


@app.put("/api/cancel_schedule/{reservation_id}")
async def cancel_schedule(reservation_id: int, request: CancelScheduleRequest, db: Session = Depends(get_db_session)):
    try:
        payload = json.loads(request.json())
        schedule = db.query(Order).filter(Order.id == reservation_id).first()
        if payload.get('refund') == True:
            #estorno manual
            yag = yagmail.SMTP(user="henriquebarreira88@gmail.com", password="yrdh enwq dkdy tsnz")
            try:
                yag.send(to="henrique.faria@arcotech.io", subject="Assunto do e-mail", contents="Corpo do e-mail")
                print("Email enviado com sucesso!")
            except Exception as e:
                print(f"Erro ao enviar e-mail: {e}")
        else:
            #expira link no pagseguro
            if not schedule:
                raise HTTPException(status_code=404, detail="Reserva não encontrada")

            # Se houver um link de pagamento, expira a preferência no Mercado Pago
            if schedule.payment_link:
                preference_id = get_preference_id(schedule.payment_link)  # Extrai o ID da preferência do link

                data = {
                    "expiration_date_from": "2000-01-01T00:00:00Z",
                    "expiration_date_to": "2000-01-01T00:00:00Z"
                }

                result = mp.preference().update(preference_id, data)

                if "response" not in result or result["response"].get("id") != preference_id:
                    raise HTTPException(status_code=500, detail="Erro ao expirar pagamento no Mercado Pago")

        # Atualiza a reserva no banco de dados
        schedule.pending = False
        schedule.payment_link = None
        schedule.active = False
        db.commit()

        return {"message": f"Reserva {reservation_id} cancelada e pagamento expirado no Mercado Pago!"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao cancelar reserva: " + str(e))
    finally:
        db.close()

@app.post("/api/webhook/payment")
async def payment_webhook(request: Request, db: Session = Depends(get_db_session)):
    try:
        payload = await request.json()
        payment_id = payload.get("data", {}).get("id")

        if not payment_id:
            raise HTTPException(status_code=400, detail="ID do pagamento ausente")

        # 🔍 Buscar detalhes do pagamento no Mercado Pago
        payment_info = mp.payment().get(payment_id)

        if "error" in payment_info:
            raise HTTPException(status_code=500, detail=f"Erro ao buscar detalhes do pagamento: {payment_info['error']}")

        payment_data = payment_info.get("response", {})
        reference_id = payment_data.get("external_reference")
        status = payment_data.get("status")

        if not reference_id:
            raise HTTPException(status_code=400, detail="external_reference ausente nos detalhes do pagamento")

        # Busca a reserva no banco de dados
        schedule = db.query(Order).filter(Order.id == reference_id).first()
        if not schedule:
            raise HTTPException(status_code=404, detail="Reserva não encontrada")

        # Se o pagamento foi aprovado, gera o recibo
        if status == "approved":
            schedule.pending = False
            db.commit()

            # 📝 Gerar o recibo
            receipt_path = generate_receipt(schedule)

            # 📩 Enviar o recibo por e-mail
            email = schedule.user.email
            yag = yagmail.SMTP(user="henriquebarreira88@gmail.com", password="yrdh enwq dkdy tsnz")
            yag.send(
                to=email,
                subject="Pagamento Aprovado! Seu recibo está anexado",
                contents="Seu pagamento foi identificado e sua reserva foi confirmada com sucesso! Recibo anexado.",
                attachments=receipt_path
            )

            return {"message": "Pagamento confirmado, reserva atualizada e recibo enviado!"}
        else:
            return {"message": f"Status do pagamento: {status} - Nenhuma ação necessária"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao processar webhook: {str(e)}")    

def generate_receipt(schedule):
    try:
        # Criar um arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            receipt_path = temp_file.name

            # Criar o PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Recibo de Pagamento", ln=True, align='C')
            pdf.ln(10)  # Adiciona uma linha em branco
            pdf.cell(200, 10, txt=f"ID da Reserva: {schedule.id}", ln=True)
            pdf.cell(200, 10, txt=f"Espaço: {schedule.space.name}", ln=True)
            pdf.cell(200, 10, txt=f"Data da Reserva: {schedule.schedule_date.strftime('%d/%m/%Y')}", ln=True)
            pdf.cell(200, 10, txt=f"Unidade: {schedule.user.username}", ln=True)
            pdf.cell(200, 10, txt=f"Email: {schedule.user.email}", ln=True)
            pdf.cell(200, 10, txt="Status: Pago", ln=True)

            # Salvar o arquivo PDF no arquivo temporário
            pdf.output(receipt_path)

            return receipt_path
    except Exception as e:
        # Se ocorrer um erro, retorna uma mensagem de erro
        print(f"Erro ao gerar o recibo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar o recibo: {str(e)}")


@app.get("/generate_pdf")
async def generate_pdf():
    try:
        # Cria um caminho para o PDF gerado
        pdf_filename = "/tmp/recibo_simples.pdf"  # Usar /tmp para ambientes como Heroku
        
        # Cria um objeto FPDF
        pdf = FPDF()
        pdf.add_page()
        
        # Define o tipo de fonte e tamanho
        pdf.set_font("Arial", size=12)
        
        # Adiciona um texto no PDF
        pdf.cell(200, 10, txt="Recibo de Pagamento", ln=True, align="C")
        pdf.ln(10)  # Adiciona uma linha em branco
        pdf.cell(200, 10, txt="Pagamento realizado com sucesso!", ln=True, align="C")
        
        # Salva o arquivo PDF
        pdf.output(pdf_filename)
        print('PDF gerado com sucesso')

        # Retorna o arquivo gerado como resposta
        return FileResponse(pdf_filename, media_type='application/pdf', filename="recibo_simples.pdf")
    
    except Exception as e:
        # Retorna um erro HTTP 500 em caso de falha, com a mensagem de erro
        print(f"Erro ao gerar PDF: {e}")  # Log do erro para depuração
        raise HTTPException(status_code=500, detail=f"Erro ao gerar o PDF: {str(e)}")

@app.post("/api/generate_receipt")
async def download_receipt(request: Request, db: Session = Depends(get_db_session)):
    try:
        payload = await request.json()
        schedule_id = payload.get("schedule_id")
        schedule = db.query(Order).filter(Order.id == schedule_id).first()
        receipt_path = generate_receipt(schedule)

        return FileResponse(receipt_path, media_type='application/pdf', filename="recibo_de_pagamento.pdf")
    
    except Exception as e:
        # Retorna um erro HTTP 500 em caso de falha, com a mensagem de erro
        print(f"Erro ao gerar PDF: {e}")  # Log do erro para depuração
        raise HTTPException(status_code=500, detail=f"Erro ao gerar o PDF: {str(e)}")


@app.post("/api/baixa_manual")
async def baixa_manual(request: Request, db: Session = Depends(get_db_session)):
    try:
        payload = await request.json()
        schedule_id = payload.get("schedule_id")
        schedule = db.query(Order).filter(Order.id == schedule_id).first()
        schedule.pending = False
        db.commit()
        db.refresh(schedule)

        return {"message": "Baixa manual efetuada com sucesso!"}
    
    except Exception as e:
        # Retorna um erro HTTP 500 em caso de falha, com a mensagem de erro
        print(f"Erro ao realizar baixa manual: {e}")  # Log do erro para depuração
        raise HTTPException(status_code=500, detail=f"Erro ao realizar baixa manual: {str(e)}")



@app.get("/")
@app.get("/{full_path:path}")
def serve_frontend(full_path: str = None):
    # Caminho para o arquivo index.html
    frontend_path = Path(os.getcwd()) / "FrontEnd" / "dist" / "index.html"

    if frontend_path.exists():
        return FileResponse(frontend_path)
    else:
        raise RuntimeError(f"File at path {frontend_path} does not exist.")