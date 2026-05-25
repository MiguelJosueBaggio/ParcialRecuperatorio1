from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from decimal import Decimal
from datetime import datetime

if TYPE_CHECKING:
    from app.modules.DetallePedido.models import DetallePedido
    from app.modules.EstadoPedido.models import EstadoPedidoModel


class Pedido(SQLModel, table=True):
    __tablename__ = "pedido"

    id: Optional[int] = Field(default=None, primary_key=True)

    usuario_id: Optional[int] = Field(
        default=None,
        foreign_key="usuario.id"
    )
    
    direccion_id: Optional[int] = Field(default=None)#cambiar cuando esté la tabla direccion

    estado_codigo: str = Field(
        foreign_key="estado_pedido.codigo",
        max_length=20
    )

    forma_pago_codigo: Optional[str] = Field(default=None, max_length=20) #cambiar cuando esté la tabla forma_pago

    subtotal: Decimal = Field(default=0.0, ge=0)
    descuento: Decimal = Field(default=0.0, ge=0)
    total: Decimal = Field(default=0.0, ge=0)

    notas: Optional[str] = Field(
        default=None,
        max_length=500
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )

    deleted_at: Optional[datetime] = Field(default=None)

    is_active: bool = Field(default=True)

    detalles_pedido: List["DetallePedido"] = Relationship(back_populates="pedido")

    estado_pedido: Optional["EstadoPedidoModel"] = Relationship(
        back_populates="pedidos"
    )