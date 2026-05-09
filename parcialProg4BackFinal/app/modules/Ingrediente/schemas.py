from typing import Optional, List

from sqlmodel import SQLModel,Field

from enum import Enum

#enums unidad


# Base

    

##Creador

class IngredienteCreate(SQLModel):
    nombre:str = Field(min_length=2,max_length=100)
    descripcion:str 
    es_alergeno: bool = Field(default=False)
    producto_ids: List[int] = Field(default_factory=list)

   


#modificacion patch

class IngredienteUpsate(SQLModel):
    nombre : Optional[str]=  Field(default=None , min_length=2,max_length=100)
    descripcion:Optional[str]=None
    es_alergeno:Optional[bool]=None
    
    is_active: Optional[bool]= None
    producto_ids: Optional[List[int]] = None  # lista de IDs de productos asociados


    ##Saliida

class IngredientePublic(SQLModel):
    id: int 
    nombre: str
    descripcion:str
    es_alergeno: bool
    is_active:bool
    producto_ids: List[int]=Field(default_factory=list)    

class IngredienteList(SQLModel):
    data:List[IngredientePublic]
    total:int