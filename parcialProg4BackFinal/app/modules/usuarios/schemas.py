from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from app.modules.Direccion_Entrega.schema import DireccionPublic, DireccionCreate,  DireccionUpdate  


class UserCreate(SQLModel):
    """Datos para registrar un nuevo usuario. El rol se asigna automáticamente como CLIENT."""
    nombre: str = Field(max_length=80)
    apellido: str = Field(max_length=80)
    email: EmailStr
    celular: Optional[str] = Field(default=None, max_length=20)
    password: str = Field(min_length=8)
    direcciones: list[DireccionCreate] = Field(default_factory=list)


class UserPublic(SQLModel):
    """Vista pública del usuario — excluye password_hash."""
    id: int
    nombre: str
    apellido: str
    email: str
    celular: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    direcciones: list[DireccionPublic] = Field(default_factory=list)    
    model_config = {"from_attributes": True}


class Token(SQLModel):
    """Respuesta del endpoint /token."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos hasta expiración