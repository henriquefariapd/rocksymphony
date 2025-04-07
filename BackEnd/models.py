from sqlalchemy import ForeignKey, create_engine, Column, Integer, String, Date, Boolean
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
import os

# Base para os modelos do SQLAlchemy
Base = declarative_base()

# Tabela de associação entre Order e Product
class OrderProduct(Base):
    __tablename__ = "order_products"
    
    order_id = Column(Integer, ForeignKey("orders.id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    quantity = Column(Integer, default=1)  # Se precisar controlar a quantidade do produto
    
    order = relationship("Order", backref="products")  # Usando backref para o relacionamento inverso
    product = relationship("Product", backref="orders")  # Usando backref para o relacionamento inverso

# Modelo de Configuração do Namespace
class NamespaceConfig(Base):
    __tablename__ = "namespaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    has_pagseguro = Column(Boolean, default=True)

# Modelo de Usuário
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    
    orders = relationship("Order", back_populates="user")
    shoppingcarts = relationship("ShoppingCart", back_populates="user")

# Modelo de Produto
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    artist = Column(String, index=True, nullable=False)
    description = Column(String, index=True, nullable=False)
    valor = Column(Integer, nullable=False)
    remaining = Column(Integer, nullable=False)
    image_path = Column(String, nullable=True)
    
    shoppingcarts = relationship("ShoppingCartProduct", back_populates="product")  # Relacionamento com carrinho
    # Não precisamos mais de "orders" explicitamente aqui, pois já estamos usando backref no "OrderProduct"

# Modelo de Pedido
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_date = Column(Date, index=True, nullable=False)  # Data do pedido
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # Referência ao Usuário
    payment_link = Column(String, nullable=True)
    pending = Column(Boolean, default=True)
    active = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="orders")
    # A relação com produtos agora é mapeada por meio da tabela OrderProduct, via backref

# Modelo de Carrinho de Compras
class ShoppingCart(Base):
    __tablename__ = "shoppingcarts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="shoppingcarts")
    
    products = relationship("ShoppingCartProduct", back_populates="shoppingcart")  # Novo relacionamento com produtos do carrinho

# Tabela de associação entre ShoppingCart e Product
class ShoppingCartProduct(Base):
    __tablename__ = "shoppingcart_products"
    
    shoppingcart_id = Column(Integer, ForeignKey("shoppingcarts.id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    quantity = Column(Integer, default=1)  # Quantidade de produtos no carrinho
    
    shoppingcart = relationship("ShoppingCart", back_populates="products")
    product = relationship("Product", back_populates="shoppingcarts")

# Configuração do banco de dados SQLite
raw_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")
if raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql://", 1)
DATABASE_URL = raw_url

# Criação do engine e da sessão
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criação das tabelas no banco de dados
Base.metadata.create_all(bind=engine)
