from typing import Optional, List, Optional

from sqlmodel import SQLModel,Field
from decimal import Decimal



from datetime import datetime

class HistorialEstadoPedidoPublic(SQLModel):

    id:int
    pedido_id:int

    estado_desde: Optional[str] = None
    estado_hacia:str

    usuario_id: Optional[int] = None
    motivo:str | None = None
    created_at: datetime

class HistorialEstadoPedidoList(SQLModel):
    data: List[HistorialEstadoPedidoPublic]
    total: int