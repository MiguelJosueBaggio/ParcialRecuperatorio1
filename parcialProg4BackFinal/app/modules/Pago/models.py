from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import BigInteger
from decimal import Decimal
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from app.modules.Pedido.models import Pedido


class EstadoPago(str, Enum):
    """
    Estado interno (de negocio) del intento de pago. No confundir con
    estado_codigo del Pedido (esos son PENDIENTE/CONFIRMADO/.../ENTREGADO/
    CANCELADO) ni con mp_status (el status crudo que devuelve MercadoPago).

    Este enum es el resultado de mapear mp_status -> EstadoPago.
    """
    PENDIENTE = "PENDIENTE"
    EN_PROCESO = "EN_PROCESO"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"
    CANCELADO = "CANCELADO"


class Pago(SQLModel, table=True):
    __tablename__ = "pago"

    id: Optional[int] = Field(default=None, primary_key=True)

    pedido_id: int = Field(foreign_key="pedido.id", index=True)

    monto: Decimal = Field(default=Decimal("0.00"), ge=0)

    # Estado de NEGOCIO (mapeado desde mp_status). Esto es lo que usa
    # el resto del código para decidir si avanzar el Pedido.
    estado: EstadoPago = Field(default=EstadoPago.PENDIENTE, max_length=20)

    # external_reference que se envía a MP al crear la preferencia.
    # Es la clave para vincular el webhook/retorno con el pedido interno.
    external_reference: str = Field(index=True, unique=True, max_length=80)

    # Clave de idempotencia por intento de pago (header x-idempotency-key
    # al crear la preferencia). Evita pagos duplicados si el usuario recarga.
    idempotency_key: str = Field(max_length=36, unique=True, index=True)

    # Convención: si la columna empieza con mp_, es un espejo de lo que
    # dice la API de MP. El resto son datos propios del negocio.
    mp_preference_id: Optional[str] = Field(default=None, max_length=255)
    mp_init_point: Optional[str] = Field(default=None, max_length=500)
    mp_payment_id: Optional[int] = Field(default=None, sa_type=BigInteger, index=True)
    mp_merchant_order_id: Optional[int] = Field(default=None, sa_type=BigInteger)
    mp_status: Optional[str] = Field(default=None, max_length=50)
    mp_status_detail: Optional[str] = Field(default=None, max_length=100)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )

    pedido: Optional["Pedido"] = Relationship(back_populates="pagos")