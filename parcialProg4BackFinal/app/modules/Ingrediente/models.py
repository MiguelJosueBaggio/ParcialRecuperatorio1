from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, ForeignKey, Integer
from decimal import Decimal
if TYPE_CHECKING:
    from app.modules.Producto.models import Producto

                                                      
class productoIngredienteLink(SQLModel, table=True):

    __tablename__= "producto_ingrediente_link"

    ingrediente_id: int = Field(
        sa_column=Column(Integer,
            ForeignKey("ingrediente.id", ondelete= "CASCADE"),
             primary_key=True,
            nullable=False,))

    producto_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("producto.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        )
    )
    cantidad:Decimal=Field(default=0.0,ge=0)
    unidad_medida_id: Optional[int] = Field(default=None, foreign_key="Unidad_medida.id")
    es_removible:bool = Field(default=True)
    







class Ingrediente(SQLModel, table=True):
    __tablename__= "ingrediente"
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=2, max_length=100, unique=True, index=True)
    descripcion:Optional [str] 
    es_alergeno:bool = Field(default=True)
    is_active: bool = Field(default=True)
    
    


   

    productos:List["Producto"]= Relationship(
        back_populates="ingredientes",
        link_model=productoIngredienteLink,)
