from typing import Optional,List
from sqlmodel import SQLModel,Field
from datetime import datetime


class CategoriaCreate(SQLModel):
    nombre: str = Field(unique=True,min_length=1,max_length=100)
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    
    parent_id: Optional[int] = None




class CategoriaUpDate(SQLModel):
     
    nombre: Optional[str] =Field(unique=True,min_length=1,max_length=100,default=None)
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool]= None


class CategoriaPublic(SQLModel):
    
    id: int
    nombre:str
    descripcion:str
    imagen_url:str
    parent_id: Optional[int] = None
    is_active: bool 
    subcategorias: List["CategoriaPublic"] = []
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

class CategoriaList(SQLModel):

    data:List[CategoriaPublic]
    total:int
