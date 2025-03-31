from sqlalchemy import ForeignKey, create_engine, Column, Integer, String, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import os

# Base para os modelos do SQLAlchemy
Base = declarative_base()

# Modelo de NamespaceConfig (configuração do namespace)
class NamespaceConfig(Base):
    __tablename__ = "namespaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    has_pagseguro = Column(Boolean, default=True)
    has_pagarme = Column(Boolean, default=False)
    max_payment_time = Column(Integer, default=1)
    min_schedule_interval = Column(Integer, index=True, default=3)
    consider_last_schedule = Column(Boolean, default=True)

    # Relacionamento inverso com User e Space
    users = relationship("User", back_populates="namespace_config")
    spaces = relationship("Space", back_populates="namespace_config")

# Modelo de Usuário
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    # Alterado para ser uma chave estrangeira para NamespaceConfig
    namespace_id = Column(Integer, ForeignKey('namespaces.id'), index=True)
    is_admin = Column(Boolean, default=False)
    schedules = relationship("Schedule", back_populates="user")

    # Relacionamento com o NamespaceConfig
    namespace_config = relationship("NamespaceConfig", back_populates="users")

# Modelo de Space (Espaço)
class Space(Base):
    __tablename__ = "spaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    # Alterado para ser uma chave estrangeira para NamespaceConfig
    namespace_id = Column(Integer, ForeignKey('namespaces.id'), index=True)
    valor = Column(Integer)  # Preço de aluguel
    min_days = Column(Integer)

    # Relacionamento com o NamespaceConfig
    namespace_config = relationship("NamespaceConfig", back_populates="spaces")

    # Relacionamento com o modelo Schedule
    schedules = relationship("Schedule", back_populates="space")

# Modelo de Schedule (Agendamento)
class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    schedule_date = Column(Date, index=True)  # Data do agendamento
    space_id = Column(Integer, ForeignKey('spaces.id'), index=True)  # Referência ao Space
    user_id = Column(Integer, ForeignKey('users.id'), index=True)  # Referência ao User

    space = relationship("Space", back_populates="schedules")
    user = relationship("User", back_populates="schedules")
    payment_link = Column(String, nullable=True)
    pending = Column(Boolean, default=True)
    active = Column(Boolean, default=True)

# Configuração do banco de dados SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Criação do engine e da sessão
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criação das tabelas no banco de dados
Base.metadata.create_all(bind=engine)
