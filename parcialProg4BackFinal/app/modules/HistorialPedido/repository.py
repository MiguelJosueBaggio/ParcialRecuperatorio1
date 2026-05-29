from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.HistorialPedido.models import HistorialEstadoPedido
from typing import Optional
class HistorialEstadoPedidoRepository(BaseRepository[HistorialEstadoPedido]):
    ##Inicializo el repositorio 
    def __init__(self, session:Session)-> None:
              super().__init__(session, HistorialEstadoPedido)
