from typing import Optional, List

from sqlmodel import SQLModel,Field
from decimal import Decimal

from enum import Enum

#enums unidad


# Base

    

##Creador

class IngredienteCreate(SQLModel):
    nombre:str = Field(min_length=2,max_length=100)
    descripcion:str 
    es_alergeno: bool = Field(default=False)
    producto_ids: List[int] = Field(default_factory=list)
    stock_cantidad:int = Field(ge=0,default=0)
   


#modificacion patch

class IngredienteUpsate(SQLModel):
    nombre : Optional[str]=  Field(default=None , min_length=2,max_length=100)
    descripcion:Optional[str]=None
    es_alergeno:Optional[bool]=None
    
    is_active: Optional[bool]= None
    producto_ids: Optional[List[int]] = None  # lista de IDs de productos asociados
    stock_cantidad: Optional[int] = Field(default=None, ge=0)

    ##Saliida

class IngredientePublic(SQLModel):
    id: int 
    nombre: str
    descripcion:str
    es_alergeno: bool
    stock_cantidad: int
    is_active:bool
    producto_ids: List[int]=Field(default_factory=list)    

class IngredienteList(SQLModel):
    data:List[IngredientePublic]
    total:int



class ProductoIngredienteCreate(SQLModel):
    producto_id: int
    ingrediente_id: int
    cantidad: Decimal = Field(default=0.0, ge=0)
    unidad_medida_id: Optional[int] = None
    es_removible: bool = Field(default=True)

class ProductoIngredienteUpdate(SQLModel):
    cantidad: Optional[Decimal] = Field(default=None, ge=0)
    unidad_medida_id: Optional[int] = None
    es_removible: Optional[bool] = None

class ProductoIngredientePublic(SQLModel):
    producto_id: int
    ingrediente_id: int
    cantidad: Decimal
    unidad_medida_id: Optional[int]
    es_removible: bool  

class ProductoIngredienteList(SQLModel):
    data: List[ProductoIngredientePublic]
    total: int    


