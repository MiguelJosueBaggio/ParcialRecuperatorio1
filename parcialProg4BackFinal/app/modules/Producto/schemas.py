from typing import Optional,List
from sqlmodel import SQLModel,Field
from decimal import Decimal


class ProductoCreate(SQLModel):
   
    nombre:str=      Field(min_length=2, max_length=150)
    descripcion:str
    precio_base: Decimal= Field(ge=0)
    imagenes_url: List[str] = Field(default_factory=list)
    stock_cantidad:int = Field(ge=0,default=0)
    disponible:bool = Field(default=True)
    unidad_venta_id:Optional[int]= None
    categoria_id: Optional[int]= None
    ingrediente_ids: List[int] = Field(default_factory=list)##modi

class ProductoUpdate(SQLModel):
    nombre:Optional[str]= Field(default=None,min_length=2,max_length=150)
    descripcion:Optional[str]= None
    precio_base:Optional[Decimal]=Field(default=None,ge=0)
    imagenes_url: Optional[List[str]] = None
    stock_cantidad:Optional[int]=None
    disponible:Optional[bool]=None
    is_active: Optional[bool]= None
    unidad_venta_id:Optional[int]= None
    categoria_id: Optional[int]= None
    ingrediente_ids: Optional[List[int]] = None 


class ProductoPublic(SQLModel):
    id: int 
    nombre: str
    descripcion:str
    precio_base: Decimal
    imagenes_url: List[str] = Field(default_factory=list)
    disponible:bool
    is_active:bool
    ingrediente_ids: List[int] = Field(default_factory=list)
    unidad_venta_id:Optional[int]= None
   ## ingredientes: List[int]=[]    
   ## categoria: Optional[CategoriaPublic] = None
    categoria_id: Optional[int]= None


class ProductoList(SQLModel):

    data:List[ProductoPublic]
    total:int  