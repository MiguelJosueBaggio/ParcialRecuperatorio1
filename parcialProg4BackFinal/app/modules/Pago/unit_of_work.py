from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.Pago.repository import PagoRepository
from app.modules.Pedido.repository import PedidoRepository
from app.modules.EstadoPedido.repository import EstadoPedidoRepository
from app.modules.HistorialPedido.repository import HistorialEstadoPedidoRepository
 
 
class PagoUnitofWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.pagos = PagoRepository(session)
        self.pedidos = PedidoRepository(session)
        self.estado_pedido = EstadoPedidoRepository(session)
        self.historial_estado_pedido = HistorialEstadoPedidoRepository(session)
