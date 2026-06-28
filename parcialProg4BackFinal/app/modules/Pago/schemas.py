from typing import Optional, List
from sqlmodel import SQLModel, Field
from decimal import Decimal
from app.modules.Pago.models import EstadoPago


class CrearPreferenciaRequest(SQLModel):
    pedido_id: int


class CrearPreferenciaResponse(SQLModel):
    init_point: str
    preference_id: str
    external_reference: str
    pago_id: int


class PagoPublic(SQLModel):
    id: int
    pedido_id: int
    external_reference: str
    mp_preference_id: Optional[str] = None
    mp_init_point: Optional[str] = None
    mp_payment_id: Optional[int] = None
    mp_status: Optional[str] = None
    estado: EstadoPago
    monto: Decimal = Field(default=0.0, ge=0)


class ConfirmarPagoRequest(SQLModel):
    pedido_id: int
    payment_id: Optional[str] = None


class PagoList(SQLModel):
    data: List[PagoPublic]
    total: int