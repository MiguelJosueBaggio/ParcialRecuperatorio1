from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field


class FormaPagoPublic(SQLModel):
    codigo: str
    descripcion: str
    habilitado: bool
    
class FormaPagoList(SQLModel):
    data: List[FormaPagoPublic]
    total: int