from typing import Optional, TYPE_CHECKING
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.modules.usuarios.model import Usuario


class Direccion(SQLModel, table=True):
    __tablename__ = "direccion"

    # PK
    id: Optional[int] = Field(default=None, primary_key=True)

    # FK → Usuario.id
    usuario_id: int = Field(
        foreign_key="usuario.id",
        nullable=False
    )

    # Relaciones
    usuario: Optional["Usuario"] = Relationship(
        back_populates="direcciones"
    )

    # Datos dirección
    alias: Optional[str] = Field(
        default=None,
        max_length=50
    )

    linea1: str = Field(
        nullable=False
    )

    linea2: Optional[str] = Field(
        default=None
    )

    ciudad: str = Field(
        nullable=False,
        max_length=100
    )

    provincia: Optional[str] = Field(
        default=None,
        max_length=100
    )

    codigo_postal: Optional[str] = Field(
        default=None,
        max_length=10
    )

    # Coordenadas
    latitud: Optional[Decimal] = Field(
        default=None,
        decimal_places=6,
        max_digits=9
    )

    longitud: Optional[Decimal] = Field(
        default=None,
        decimal_places=6,
        max_digits=9
    )

    es_principal: bool = Field(
        default=False,
        nullable=False
    )

    # Auditoría
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )

    deleted_at: Optional[datetime] = Field(
        default=None
    )