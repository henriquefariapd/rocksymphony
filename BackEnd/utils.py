import jwt
from datetime import datetime, timezone
from .config import SECRET_KEY  # Defina uma chave secreta segura
#from config import SECRET_KEY  # Defina uma chave secreta segura

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if datetime.now(timezone.utc) > datetime.fromtimestamp(payload["exp"], timezone.utc):
            return None  # Token expirado
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expirado
    except jwt.InvalidTokenError:
        return None  # Token inválido