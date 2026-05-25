from typing import Optional,List
from sqlmodel import SQLModel,Field
from decimal import Decimal




class DetallePedidoCreate(SQLModel):
    producto_id: int
    
    cantidad: int = Field(default=1, ge=1)
    personalizacion: List[int] = []

class DetallePedidoUpdate(SQLModel):
    producto_id: Optional[int] = None
    pedido_id: Optional[int] = None
    cantidad: Optional[int] = Field(default=None, ge=1)
   
    is_active: Optional[bool] = None

class DetallePedidoPublic(SQLModel):
    id:int
    producto_id:int
    pedido_id:int
    cantidad:int
    nombre_snapshot:str
    precio_snapshot:Decimal
    subtotal_snap:Decimal
    personalizacion:Optional[List[int]]
class DetallePedidoList(SQLModel):

    data:List[DetallePedidoPublic]
    total:int  



class PedidoCreate(SQLModel):
    usuario_id: Optional[int] = None
 #   direccion_id: Optional[int] = None
    estado_codigo:str = Field( max_length=20)
    forma_pago_codigo:str = Field(max_length=20)    
    notas: Optional[str] = Field(default=None, max_length=500)      
   

    detalles: List[DetallePedidoCreate] = Field(default_factory=list)

class PedidoUpdate(SQLModel):
    usuario_id: Optional[int] = None
  #  direccion_id: Optional[int] = None
    estado_codigo: Optional[str] = Field(default=None, max_length=20)
    forma_pago_codigo: Optional[str] = Field(default=None, max_length=20)    
    notas: Optional[str] = Field(default=None, max_length=500) 
    is_active: Optional[bool]= None

class PedidoPublic(SQLModel):
    id: int 
    usuario_id: Optional[int] = None
   # direccion_id: Optional[int] = None
    estado_codigo:str = Field( max_length=20)
    forma_pago_codigo:str = Field(max_length=20)    
    subtotal: Decimal = Field(default=0.0, ge=0)
    descuento: Decimal = Field(default=0.0, ge=0)
    total: Decimal = Field(default=0.0, ge=0)
    notas: Optional[str] = Field(default=None, max_length=500) 
    is_active: bool = Field(default=True)

class PedidoList(SQLModel):
    data:List[PedidoPublic]
    total:int

