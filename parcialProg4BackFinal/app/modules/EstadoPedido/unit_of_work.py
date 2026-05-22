from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.EstadoPedido.repository import EstadoPedidoRepository      
from app.modules.Pedido.repository import ProductoRepository

class EstadoPedidoUnitofWork(UnitOfWork):
    def __init__ (self, session:Session)-> None:
        super().__init__(session)
        self.estados_pedidos= EstadoPedidoRepository(session)
        self.productos = ProductoRepository(session)
        