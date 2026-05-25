
from typing import Optional, TYPE_CHECKING, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func



if TYPE_CHECKING:
    from app.modules.Rol.models import Rol
    from Direccion_Entrega.models import Direccion
    from app.modules.Pedido.models import Pedido
class Usuario(SQLModel, table=True):
    __tablename__ = "usuario"

    id: Optional[int] = Field(default=None, primary_key=True)

    nombre: str = Field(max_length=80, nullable=False)
    apellido: str = Field(max_length=80, nullable=False)
    email: str = Field(max_length=254, index=True, unique=True, nullable=False)
    celular: Optional[str] = Field(default=None, max_length=20)
    password_hash: str = Field(max_length=250, nullable=False)
    

    direcciones: list["Direccion"] = Relationship(
    back_populates="usuario"
)

    pedidos: List["Pedido"] = Relationship(back_populates="usuario")

    # Soft delete
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )

    # Timestamps
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    )