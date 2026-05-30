from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.HistorialPedido.repository import HistorialEstadoPedidoRepository 
from app.modules.EstadoPedido.repository import EstadoPedidoRepository

from app.modules.Producto.repository import ProductoRepository      


class HistorialEstadoPedidoUnitofWork(UnitOfWork):
    def __init__ (self, session:Session)-> None:
        super().__init__(session)
        self.historial_estado_pedido = HistorialEstadoPedidoRepository(session)
        self.productos = ProductoRepository(session)


