from sqlalchemy.orm import Session
from datetime import date
from models import NamespaceConfig, User, Space, SessionLocal
from passlib.context import CryptContext

# Função para criar um usuário (caso queira adicionar ao seu banco de dados)
def create_user(db: Session, username: str, hashed_password: str, is_admin: bool, namespace_id: int):
    user = User(username=username, hashed_password=hashed_password, is_admin=is_admin, namespace_id=namespace_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Função para criar um espaço e um agendamento
def create_data(db: Session):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(password: str):
        return pwd_context.hash(password)

    hashed_password = hash_password("password123")

    namespace1 = NamespaceConfig(name="Chacara Das Rosas", has_pagseguro=True)
    namespace2 = NamespaceConfig(name="Chacara Das Rosas", has_pagseguro=True)
    
    db.add(namespace1)
    db.commit()
    db.refresh(namespace1)

    db.add(namespace2)
    db.commit()
    db.refresh(namespace2)


    new_space = Space(name="Churrasqueira", namespace_id=namespace1.id, valor=250, min_days=30)
    new_space2 = Space(name="Piscina", namespace_id=namespace2.id, valor=50, min_days=30)
    
    db.add(new_space)
    db.commit()
    db.refresh(new_space)

    db.add(new_space2)
    db.commit()
    db.refresh(new_space2)



    create_user(db, username="usuario_admin", hashed_password=hashed_password, is_admin=True, namespace_id=namespace1.id)
    create_user(db, username="usuario_teste", hashed_password=hashed_password, is_admin=False, namespace_id=namespace1.id)

    create_user(db, username="usuario_admin2", hashed_password=hashed_password, is_admin=True, namespace_id=namespace2.id)
    create_user(db, username="usuario_teste2", hashed_password=hashed_password, is_admin=False, namespace_id=namespace2.id)

    
    print(f"Espaço 'Churrasqueira' criado com sucesso no namespace 'Chacara das Rosas'.")


# Função principal
def main():
    db = SessionLocal()


    create_data(db)

    db.close()

if __name__ == "__main__":
    main()
