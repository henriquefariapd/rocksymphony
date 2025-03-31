# schemas.py
from pydantic import BaseModel

class UserResponse(BaseModel):
    username: str
    email: str

    class Config:
        orm_mode = True  # Isso permite que o Pydantic trabalhe com modelos ORM (SQLAlchemy)

class UserCreate(BaseModel):
    username: str
    password: str
