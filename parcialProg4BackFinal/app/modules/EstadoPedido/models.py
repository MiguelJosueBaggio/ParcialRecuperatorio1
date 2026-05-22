from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.modules.Pedido.models import Pedido


class EstadoPedidoModel(SQLModel, table=True):
    __tablename__ = "estado_pedido"

    codigo: str = Field(
        primary_key=True,
        index=True,
        max_length=20
    )

    descripcion: Optional[str] = Field(
        default=None,
        max_length=80
    )

    orden: int = Field(default=0)

    es_terminal: bool = Field(default=False)

    pedidos: List["Pedido"] = Relationship(
        back_populates="estado_pedido"
    )