from sqlalchemy.orm import Session
from datetime import date
from models import NamespaceConfig, User, Product, SessionLocal
from passlib.context import CryptContext

# Função para criar um usuário (caso queira adicionar ao seu banco de dados)
def create_user(db: Session, username: str, email: str,  hashed_password: str, is_admin: bool):
    user = User(username=username, email=email, hashed_password=hashed_password, is_admin=is_admin)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Função para criar um espaço e um agendamento
def create_data(db: Session):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(password: str):
        return pwd_context.hash(password)

    hashed_password = hash_password("123")
    namespace1 = NamespaceConfig(name="Chacara Das Rosas", has_pagseguro=True)
    
    db.add(namespace1)
    db.commit()
    db.refresh(namespace1)




    new_product = Product(name="Parachutes", artist='Coldplay',description='Parachutes é o primeiro álbum do Coldplay, lançado em 2000. Ele tem músicas calmas e emotivas, como Yellow, Shiver e Trouble. O disco ajudou a banda a ficar famosa no mundo inteiro, misturando letras sentimentais com melodias suaves. Foi muito elogiado e ganhou até um Grammy como Melhor Álbum de Música Alternativa.', valor=250,  remaining=30)
    new_product1 = Product(name="Ventura", artist='Los Hermanos',description='Ventura é o terceiro álbum da banda Los Hermanos, lançado em 2003. Ele marcou uma fase mais madura da banda, com músicas que misturam rock, samba e MPB. Canções como O Vencedor, Último Romance e Cara Estranho se destacaram. O álbum foi muito elogiado por suas letras poéticas e arranjos criativos, consolidando Los Hermanos como uma das bandas mais queridas do Brasil.', valor=50, remaining=30)
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    db.add(new_product1)
    db.commit()
    db.refresh(new_product1)



    create_user(db, username="adm", email="leonahoum@gmail.com", hashed_password=hashed_password, is_admin=True)
    create_user(db, username="user", email="leonadois@gmail.com", hashed_password=hashed_password, is_admin=False)

    create_user(db, username="adm2", email="leonatres@gmail.com", hashed_password=hashed_password, is_admin=True)
    create_user(db, username="user2", email="leonaquatro@gmail.com", hashed_password=hashed_password, is_admin=False)

    
    print(f"Espaço 'Churrasqueira' criado com sucesso no namespace 'Chacara das Rosas'.")


# Função principal
def main():
    db = SessionLocal()


    create_data(db)

    db.close()

if __name__ == "__main__":
    main()
