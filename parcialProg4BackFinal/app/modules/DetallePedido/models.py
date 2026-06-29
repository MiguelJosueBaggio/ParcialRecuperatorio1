from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, ForeignKey, Integer
from decimal import Decimal
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, ARRAY, TEXT
if TYPE_CHECKING:
    from app.modules.Producto.models import Producto
    from app.modules.Pedido.models import Pedido

##Tabla DetallePedido
class DetallePedido (SQLModel,table=True):
 __tablename__= "detalle_pedido"

 id: Optional[int]= Field(default=None, primary_key=True)
 producto_id: Optional[int] = Field(default=None, foreign_key="producto.id")
 producto: Optional["Producto"] = Relationship(back_populates="detalles_pedido")
 pedido_id: Optional[int] = Field(default=None, foreign_key="pedido.id")
 cantidad: int = Field(default=1, ge=1)
 nombre_snapshot: str = Field(nullable=False, max_length=200)
 precio_snapshot: Decimal = Field(nullable=False, ge=0)
 subtotal_snap: Decimal = Field(nullable=False, ge=0)
 personalizacion: Optional[List[int]] = Field(default=None, sa_columnkwargs={"type": "INTEGER[]"})
 created_at: datetime = Field(default_factory=datetime.utcnow)
 is_active: bool = Field(default=True)