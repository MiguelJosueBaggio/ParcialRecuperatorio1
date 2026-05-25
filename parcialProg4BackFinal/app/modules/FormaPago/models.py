from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from decimal import Decimal
from datetime import datetime   
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.modules.Pedido.models import Pedido

class FormaPago(SQLModel, table=True):

    __tablename__ = "forma_pago"

    codigo: str = Field(
        primary_key=True,
        max_length=20
    )

    descripcion: str = Field(
        max_length=80
    )

    habilitado: bool = Field(
        default=True
    )

    # RELACION 1:N
    pedidos: List["Pedido"] = Relationship(
        back_populates="forma_pago"
    )