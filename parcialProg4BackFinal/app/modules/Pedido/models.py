from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, ForeignKey, Integer
from decimal import Decimal
from datetime import datetime
if TYPE_CHECKING:
    from app.modules.Producto.models import Producto
    from app.modules.DetallePedido import DetallePedido


    class Pedido (SQLModel, table=True):
        __tablename__= "pedido"

        id: Optional[int] = Field(default=None, primary_key=True)
        usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
        direccion_id: Optional[int] = Field(default=None, foreign_key="direccion.id")
        detalles_pedido: List["DetallePedido"] = Relationship(back_populates="pedido")
        estado_codigo:str = Field( max_length=20,foreign_key="estadoPedido.codigo")
        forma_pago_codigo:str = Field(max_length=20, foreign_key="formaPago.codigo")    
        subtotal: Decimal = Field(default=0.0, ge=0)
        descuento: Decimal = Field(default=0.0, ge=0)
        total: Decimal = Field(default=0.0, ge=0)
        notas: Optional[str] = Field(default=None, max_length=500)
        created_at: datetime = Field(default_factory=datetime.utcnow)
        updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
        deleted_at: Optional[datetime] = Field(default=None)
        is_active: bool = Field(default=True)   