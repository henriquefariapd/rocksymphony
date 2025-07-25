from supabase import create_client, Client

# Importações com fallback para local e Heroku
try:
    from .config import SUPABASE_URL, SUPABASE_KEY
except ImportError:
    from config import SUPABASE_URL, SUPABASE_KEY

# Inicializar o cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase_client():
    """Retorna o cliente Supabase"""
    return supabase
