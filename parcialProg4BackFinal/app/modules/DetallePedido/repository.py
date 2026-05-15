from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.Producto.models import Producto
from app.modules.DetallePedido import DetallePedido


class DetallePedidoRepository(BaseRepository[DetallePedido]):
    ##Inicializo el repositorio 

    def __init__(self, session:Session)-> None:
              super().__init__(session, DetallePedido)

    def get_active(self, offset: int = 0, limit: int = 20) -> list[DetallePedido]:
        statement = (
        select(DetallePedido)
        .where(DetallePedido.is_active == True)
        .offset(offset)
        .limit(limit)
    )
        return list(self.session.exec(statement).all())