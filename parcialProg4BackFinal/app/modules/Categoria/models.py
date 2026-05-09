from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, ForeignKey, Integer, DateTime, func

from datetime import datetime



if TYPE_CHECKING:
    from app.modules.Producto.models import Producto

class Categoria(SQLModel, table=True):
    __tablename__ = "categoria"


   # PK
    id: Optional[int] = Field(default=None, primary_key=True)

    
    # Atributos
    nombre: str = Field(index=True, nullable=False, max_length=100, sa_column_kwargs={"unique": True})
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    is_active: bool = Field(default=True)
    

    # Timestamps
    created_at: Optional[datetime] = Field(default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )

   # Relación autorreferenciada: una categoría puede tener subcategorías
    parent_id: Optional[int] = Field(default=None, foreign_key="categoria.id")
    subcategorias: List["Categoria"] = Relationship(back_populates="parent", sa_relationship_kwargs={"cascade": "all, delete"})
    parent: Optional["Categoria"] = Relationship(back_populates="subcategorias", sa_relationship_kwargs={"remote_side": "Categoria.id"})
    
    
    productos: List["Producto"] = Relationship(back_populates="categoria")
