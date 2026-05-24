from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.Producto.models import Producto
from app.modules.DetallePedido.models import DetallePedido
from app.modules.Pedido.models import Pedido    

class PedidoRepository(BaseRepository[Pedido]):
    ##Inicializo el repositorio 

    def __init__(self, session:Session)-> None:
              super().__init__(session, Pedido)

    def get_active(self, offset: int = 0, limit: int = 20) -> list[Pedido]:
        statement = (
        select(Pedido)
        .where(Pedido.is_active == True)
        .offset(offset)
        .limit(limit)
    )
        return list(self.session.exec(statement).all())
    
    def get_pedidos_by_estado(self, estado_codigo: str, offset: int = 0, limit: int = 20) -> list[Pedido]:
        statement = (
        select(Pedido)
        .where(Pedido.estado_codigo == estado_codigo)
        .offset(offset)
        .limit(limit)
    )
        return self.session.exec(statement).all()