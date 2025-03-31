Para rodar localmente, descomentar:

main.py:
    # app.mount("/assets", StaticFiles(directory=Path(os.getcwd()) / "FrontEnd" / "dist" / "assets"), name="assets")

    #from .models import Schedule, SessionLocal, Space, User
    from models import NamespaceConfig, Schedule, SessionLocal, Space, User
    #from .utils import decode_token
    from utils import decode_token
    #from .config import SECRET_KEY
    from config import SECRET_KEY


utils.py:
    #from .config import SECRET_KEY  # Defina uma chave secreta segura
    from config import SECRET_KEY  # Defina uma chave secreta segura



rodar o BackEnd: uvicorn main:app --reload
rodar o FrontEnd: npm run dev