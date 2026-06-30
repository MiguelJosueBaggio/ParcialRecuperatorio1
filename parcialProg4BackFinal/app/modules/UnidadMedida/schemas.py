from typing import List, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class UnidadMedidaPublic(SQLModel):
    id: int
    nombre: str
    simbolo: str
    tipo: str
    created_at: Optional[datetime] = None


class UnidadMedidaList(SQLModel):
    data: List[UnidadMedidaPublic]
    total: int