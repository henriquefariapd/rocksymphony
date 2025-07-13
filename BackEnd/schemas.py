# schemas.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Schemas para Artist
class ArtistBase(BaseModel):
    name: str
    origin_country: str
    members: Optional[str] = None
    formed_year: Optional[int] = None
    description: Optional[str] = None
    genre: Optional[str] = None

class ArtistCreate(ArtistBase):
    pass

class ArtistUpdate(BaseModel):
    name: Optional[str] = None
    origin_country: Optional[str] = None
    members: Optional[str] = None
    formed_year: Optional[int] = None
    description: Optional[str] = None
    genre: Optional[str] = None

class Artist(ArtistBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    username: str
    email: str

    class Config:
        orm_mode = True  # Isso permite que o Pydantic trabalhe com modelos ORM (SQLAlchemy)

class UserCreate(BaseModel):
    username: str
    password: str
