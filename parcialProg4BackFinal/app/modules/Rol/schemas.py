from typing import Optional
from sqlmodel import SQLModel, Field


class RolCreate(SQLModel):
    codigo: str = Field(max_length=20)
    nombre: str = Field(max_length=50)
    descripcion: Optional[str] = None


class RolUpdate(SQLModel):
    nombre: Optional[str] = Field(default=None, max_length=50)
    descripcion: Optional[str] = None


class RolPublic(SQLModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None

    model_config = {"from_attributes": True}