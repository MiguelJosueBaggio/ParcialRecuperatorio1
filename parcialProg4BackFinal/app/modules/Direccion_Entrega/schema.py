from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field


class DireccionCreate(SQLModel):

    usuario_id: int

    alias: Optional[str] = Field(
        default=None,
        max_length=50
    )

    linea1: str

    linea2: Optional[str] = None

    ciudad: str

    provincia: Optional[str] = None

    codigo_postal: Optional[str] = Field(
        default=None,
        max_length=10
    )

    latitud: Optional[Decimal] = None

    longitud: Optional[Decimal] = None

    es_principal: bool = False


class DireccionUpdate(SQLModel):

    alias: Optional[str] = None

    linea1: Optional[str] = None

    linea2: Optional[str] = None

    ciudad: Optional[str] = None

    provincia: Optional[str] = None

    codigo_postal: Optional[str] = None

    latitud: Optional[Decimal] = None

    longitud: Optional[Decimal] = None

    es_principal: Optional[bool] = None


class DireccionPublic(SQLModel):

    id: int

    usuario_id: int

    alias: Optional[str]

    linea1: str

    linea2: Optional[str]

    ciudad: str

    provincia: Optional[str]

    codigo_postal: Optional[str]

    latitud: Optional[Decimal]

    longitud: Optional[Decimal]

    es_principal: bool

    created_at: datetime

    updated_at: datetime



class DireccionList(SQLModel):

    items: List[DireccionPublic]
    total: int