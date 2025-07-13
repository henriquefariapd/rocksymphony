from sqlalchemy import ForeignKey, create_engine, Column, Integer, String, Boolean, DateTime, Numeric, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from datetime import datetime
import os
from dotenv import load_dotenv
import enum

load_dotenv()

# Enum para países
class CountryEnum(enum.Enum):
    BRASIL = "Brasil"
    ESTADOS_UNIDOS = "Estados Unidos"
    REINO_UNIDO = "Reino Unido"
    ALEMANHA = "Alemanha"
    FRANCA = "França"
    JAPAO = "Japão"
    CANADA = "Canadá"
    AUSTRALIA = "Austrália"
    ARGENTINA = "Argentina"
    MEXICO = "México"
    HOLANDA = "Holanda"
    SUECIA = "Suécia"
    NORUEGA = "Noruega"
    DINAMARCA = "Dinamarca"
    FINLANDIA = "Finlândia"
    ITALIA = "Itália"
    ESPANHA = "Espanha"
    PORTUGAL = "Portugal"
    BELGICA = "Bélgica"
    AUSTRIA = "Áustria"
    SUICA = "Suíça"
    POLONIA = "Polônia"
    REPUBLICA_TCHECA = "República Tcheca"
    HUNGRIA = "Hungria"
    GRECIA = "Grécia"
    TURQUIA = "Turquia"
    RUSSIA = "Rússia"
    CHINA = "China"
    COREIA_DO_SUL = "Coreia do Sul"
    INDIA = "Índia"
    TAILANDIA = "Tailândia"
    SINGAPURA = "Singapura"
    NOVA_ZELANDIA = "Nova Zelândia"
    AFRICA_DO_SUL = "África do Sul"
    CHILE = "Chile"
    COLOMBIA = "Colômbia"
    PERU = "Peru"
    URUGUAI = "Uruguai"
    PARAGUAI = "Paraguai"
    BOLIVIA = "Bolívia"
    EQUADOR = "Equador"
    VENEZUELA = "Venezuela"
    CUBA = "Cuba"
    JAMAICA = "Jamaica"
    OUTRO = "Outro"

# Base para os modelos do SQLAlchemy
Base = declarative_base()

class Artist(Base):
    __tablename__ = "artists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    origin_country = Column(String(100), nullable=False)
    members = Column(Text)
    formed_year = Column(Integer)
    description = Column(Text)
    genre = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com produtos
    products = relationship("Product", back_populates="artist")

# Modelo de Usuário (sincronizado com Supabase Auth)
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)  # UUID do Supabase Auth
    usuario = Column(String(50), unique=True, index=True, nullable=True)  # Campo usuario (display name)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    orders = relationship("Order", back_populates="user")
    shoppingcarts = relationship("ShoppingCart", back_populates="user")
    addresses = relationship("Address", back_populates="user")

# Modelo de Produto (CDs de Rock)
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), index=True, nullable=False)  # Nome do álbum
    # artist = Column(String(200), index=True, nullable=False)  # Nome do artista/banda - REMOVIDO
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=True)  # Relação com artista
    description = Column(Text, nullable=True)  # Descrição do álbum
    valor = Column(Numeric(10, 2), nullable=False)  # Preço em decimal
    remaining = Column(Integer, nullable=False, default=0)  # Estoque disponível
    image_path = Column(String(500), nullable=True)  # Caminho da imagem
    genre = Column(String(100), nullable=True)  # Gênero musical
    release_year = Column(Integer, nullable=True)  # Ano de lançamento
    label = Column(String(100), nullable=True)  # Gravadora
    reference_code = Column(String(100), nullable=True)  # Código de referência
    stamp = Column(String(100), nullable=True)  # Selo
    country = Column(Enum(CountryEnum), nullable=True)  # País de origem
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    artist = relationship("Artist", back_populates="products")
    shoppingcarts = relationship("ShoppingCartProduct", back_populates="product")

# Modelo de Pedido
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False, index=True)
    payment_link = Column(String(500), nullable=True)
    pending = Column(Boolean, default=True)
    sent = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    total_amount = Column(Numeric(10, 2), nullable=False, default=0)
    shipping_cost = Column(Numeric(10, 2), nullable=False, default=0)  # Valor do frete
    tracking_code = Column(String(255), nullable=True)  # Código de rastreamento dos correios
    
    user = relationship("User", back_populates="orders")
    address = relationship("Address")
    products = relationship("OrderProduct", back_populates="order")

# Modelo de Carrinho de Compras
class ShoppingCart(Base):
    __tablename__ = "shoppingcarts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="shoppingcarts")
    products = relationship("ShoppingCartProduct", back_populates="shoppingcart")

# Tabela de associação entre Order e Product
class OrderProduct(Base):
    __tablename__ = "order_products"
    
    order_id = Column(Integer, ForeignKey("orders.id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    quantity = Column(Integer, default=1, nullable=False)
    price_at_time = Column(Numeric(10, 2), nullable=False)  # Preço no momento da compra
    
    order = relationship("Order", back_populates="products")
    product = relationship("Product")

# Tabela de associação entre ShoppingCart e Product
class ShoppingCartProduct(Base):
    __tablename__ = "shoppingcart_products"
    
    shoppingcart_id = Column(Integer, ForeignKey("shoppingcarts.id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    quantity = Column(Integer, default=1, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    shoppingcart = relationship("ShoppingCart", back_populates="products")
    product = relationship("Product", back_populates="shoppingcarts")

# Modelo de Endereços
class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    cep = Column(String(10), nullable=False)
    street = Column(String(255), nullable=False)
    number = Column(String(20), nullable=False)
    complement = Column(String(100), nullable=True)
    neighborhood = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False, default="Brasil")
    receiver_name = Column(String(255), nullable=False)
    full_address = Column(Text, nullable=False)  # Endereço completo formatado
    is_default = Column(Boolean, default=False)  # Endereço padrão
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="addresses")

# Configuração do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Criação do engine e da sessão
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Função para obter a sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Só cria as tabelas se não for PostgreSQL (Supabase)
if not DATABASE_URL.startswith("postgresql"):
    Base.metadata.create_all(bind=engine)
