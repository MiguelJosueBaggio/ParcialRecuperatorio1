from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.HistorialPedido.models import HistorialEstadoPedido
from typing import Optional
from sqlalchemy import func
class HistorialEstadoPedidoRepository(BaseRepository[HistorialEstadoPedido]):
    ##Inicializo el repositorio 
    def __init__(self, session:Session)-> None:
              super().__init__(session, HistorialEstadoPedido)
    

    def count_sin_filtro(self):
     stmt = (
        select(func.count())
        .select_from(self.model)
        )

     return self.session.exec(stmt).one()