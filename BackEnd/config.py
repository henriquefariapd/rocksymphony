# config.py
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = "19fbc979b00de9b147dac8d66403826ded6341465ef2002d740bc4a126054782"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configurações do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Verificação das variáveis de ambiente
if not SUPABASE_URL or not SUPABASE_KEY or not DATABASE_URL:
    print("ERRO: Variáveis de ambiente do Supabase não configuradas!")
    print(f"SUPABASE_URL: {SUPABASE_URL}")
    print(f"SUPABASE_KEY: {'*' * 20 if SUPABASE_KEY else 'None'}")
    print(f"DATABASE_URL: {'*' * 20 if DATABASE_URL else 'None'}")
