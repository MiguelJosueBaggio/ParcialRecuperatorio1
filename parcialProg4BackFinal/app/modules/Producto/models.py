from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, ForeignKey, Integer
from decimal import Decimal
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, ARRAY, TEXT
from app.modules.Ingrediente.models import productoIngredienteLink
from app.modules.DetallePedido.models import DetallePedido
if TYPE_CHECKING: ##Evitar refercnias circualreas
    from app.modules.Ingrediente.models import Ingrediente
    from app.modules.Categoria.models import Categoria
    from app.modules.DetallePedido.models import DetallePedido

##Tabala producto
class Producto (SQLModel,table=True):

    __tablename__= "producto"

    id: Optional[int]= Field(default=None, primary_key=True)
    unidad_venta_id:  Optional[int] = Field(default=None, foreign_key="Unidad_medida.id")
    nombre: str = Field(index=True)
    descripcion :Optional[str]= Field(default=None)
    precio_base: Decimal=Field(default=0.0,ge=0)
    imagenes_url: List[str] = Field(
    default_factory=list,
    sa_column=Column(ARRAY(TEXT))
)
    
    stock_cantidad:int = Field(default=0,ge=0)
    disponible:bool = Field(default=True)
    is_active: bool = Field(default=True)
   
   ###Relacion 1 categoria muchos productos
    categoria_id: Optional[int] = Field(default=None, foreign_key="categoria.id")
    categoria: Optional["Categoria"] = Relationship(back_populates="productos")

    ###Relacion 1 producto muchos detalles pedido       
    detalles_pedido: List["DetallePedido"] = Relationship(back_populates="producto")

###Relacion muchos a muchos con ingredientes
    ingredientes:List["Ingrediente"]= Relationship(
        back_populates="productos",
        link_model=productoIngredienteLink,)



