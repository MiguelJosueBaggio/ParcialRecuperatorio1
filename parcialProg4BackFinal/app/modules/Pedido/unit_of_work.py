from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.Ingrediente.repository import IngredienteRepository
from app.modules.DetallePedido.repository import DetallePedidoRepository
from app.modules.Producto.repository import ProductoRepository
from app.modules.Pedido.repository import PedidoRepository
from app.modules.HistorialPedido.repository import HistorialEstadoPedidoRepository
class PedidoUnitofWork(UnitOfWork):
    def __init__ (self, session:Session)-> None:
        super().__init__(session)
        self.pedidos = PedidoRepository(session) 
        self.productos = ProductoRepository(session)
        self.detalle_pedidos = DetallePedidoRepository(session)
        self.ingredientes = IngredienteRepository(session)
        self.historial_estado_pedido = HistorialEstadoPedidoRepository(session)