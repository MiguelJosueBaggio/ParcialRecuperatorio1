from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.EstadoPedido.models import EstadoPedidoModel
from app.modules.Pedido.models import Pedido
class EstadoPedidoRepository(BaseRepository[EstadoPedidoModel]):
    ##Inicializo el repositorio 
    def __init__(self, session:Session)-> None:
              super().__init__(session, EstadoPedidoModel)
    
    def get_by_codigo(self, codigo: str) -> EstadoPedidoModel | None:
        return self.session.exec(
            select(EstadoPedidoModel).where(EstadoPedidoModel.codigo == codigo)
        ).first()   
