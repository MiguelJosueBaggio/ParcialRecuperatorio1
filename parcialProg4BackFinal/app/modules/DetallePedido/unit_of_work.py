from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.DetallePedido.repository import DetallePedidoRepository
from app.modules.Producto.repository import ProductoRepository
from app.modules.Pedido.repository import PedidoRepository

class DetallePedidoUnitofWork(UnitOfWork):
    def __init__ (self, session:Session)-> None:
        super().__init__(session)
        self.detalle_pedidos = DetallePedidoRepository(session) 
        self.productos = ProductoRepository(session)
        self.pedidos = PedidoRepository(session)
        