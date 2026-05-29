from typing import Optional, TYPE_CHECKING, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
if TYPE_CHECKING:
    from app.modules.usuarios.model import Usuario
    from app.modules.Pedido.models import Pedido
    from app.modules.EstadoPedido.models import EstadoPedidoModel
class HistorialEstadoPedido(SQLModel, table=True):
    __tablename__ = "historial_estado_pedido"
    # PK
    id: Optional[int] = Field(default=None, primary_key=True)
    # FK → Pedido.id (CASCADE)
    pedido_id: int = Field(
        foreign_key="pedido.id",
        nullable=False
    )
    # FK → EstadoPedido.codigo (NULL = estado inicial)
    estado_desde: Optional[str] = Field(
        default=None,
        foreign_key="estado_pedido.codigo",
        max_length=20
    )
    # FK → EstadoPedido.codigo (NN)
    estado_hacia: str = Field(
        foreign_key="estado_pedido.codigo",
        nullable=False,
        max_length=20
    )
    # FK de trazabilidad → Usuario.id (NULL = sistema)
    usuario_id: Optional[int] = Field(
        default=None,
        foreign_key="usuario.id"
    )
    # Atributos
    motivo: Optional[str] = Field(default=None)
    # Auditoría (append-only: sin updated_at ni deleted_at)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    # Relaciones
    pedido: Optional["Pedido"] = Relationship(back_populates="historial_estados")
    usuario: Optional["Usuario"] = Relationship(back_populates="historial_estados_pedido")
    
    estado_desde_rel: Optional["EstadoPedidoModel"] = Relationship(
    back_populates="historial_desde",
    sa_relationship_kwargs={
        "foreign_keys": "HistorialEstadoPedido.estado_desde"
    }
)

    estado_hacia_rel: "EstadoPedidoModel" = Relationship(
    back_populates="historial_hacia",
    sa_relationship_kwargs={
        "foreign_keys": "HistorialEstadoPedido.estado_hacia"
    }
)