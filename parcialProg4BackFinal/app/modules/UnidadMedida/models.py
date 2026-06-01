from typing import Optional, TYPE_CHECKING, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

from sqlmodel import SQLModel, Field 
from sqlalchemy import Column, DateTime, func
if TYPE_CHECKING:
    from app.modules.Producto.models import Producto
    from app.modules.Ingrediente.models import productoIngredienteLink

class UnidadMedida(SQLModel, table=True):
    """
    Catálogo de unidades de medida.
    Se usa en dos lugares:
      - Producto.unidad_venta_id → unidad en que se vende el producto (ej: kg, litro, pieza)
      - ProductoIngrediente.unidad_medida_id → unidad del ingrediente dentro del producto

    El campo 'tipo' agrupa las unidades para filtrar y habilitar conversiones:
      - masa: kilogramo (kg), gramo (g)
      - volumen: litro (L), mililitro (mL)
      - unidad: pieza (u), docena (doc)
      - area: metro cuadrado (m²)
    """
    __tablename__ = "unidad_medida"

    id: Optional[int] = Field(default=None, primary_key=True)

    nombre: str = Field( max_length=50, unique=True, nullable=False)
    simbolo: str = Field( max_length=10, unique=True, nullable=False)
    tipo: str = Field( max_length=20, nullable=False)

    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False
        )
    )

    productos_venta: list["Producto"] = Relationship(back_populates="unidad_venta")
    ingredientes: list["productoIngredienteLink"] = Relationship(back_populates="unidad_medida")