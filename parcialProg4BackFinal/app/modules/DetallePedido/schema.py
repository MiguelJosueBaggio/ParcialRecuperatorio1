from typing import Optional,List
from sqlmodel import SQLModel,Field
from decimal import Decimal


class DetallePedidoCreate(SQLModel):
    producto_id: int
    pedido_id: int
    cantidad: int = Field(default=1, ge=1)
    nombre_snapshot: str = Field(nullable=False, max_length=200)
    precio_snapshot: Decimal = Field(nullable=False, ge=0)
   ## subtotal_snap: Decimal = Field(nullable=False, ge=0)
    personalizacion: Optional[List[int]] = Field(default=None, sa_columnkwargs={"type": "INTEGER[]"})

class DetallePedidoUpdate(SQLModel):
    producto_id: Optional[int] = None
    pedido_id: Optional[int] = None
    cantidad: Optional[int] = Field(default=None, ge=1)
   # nombre_snapshot: Optional[str] = Field(default=None, max_length=200)
    #precio_snapshot: Optional[Decimal] = Field(default=None, ge=0)
  ##  subtotal_snap: Optional[Decimal] = Field(default=None, ge=0)
    #personalizacion: Optional[List[int]] = Field(default=None, sa_columnkwargs={"type": "INTEGER[]"})
    is_active: Optional[bool] = None

class DetallePedidoPublic(SQLModel):
    id:int
    producto_id:int
    pedido_id:int
    cantidad:int
    nombre_snapshot:str
    precio_snapshor:Decimal
    subtotal_snap:Decimal
    personalizacion:Optional[List[int]]
class DetallePedidoList(SQLModel):

    data:List[DetallePedidoList]
    total:int  