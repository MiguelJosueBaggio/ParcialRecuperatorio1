from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.Direccion_Entrega.repository import DireccionEntregaRepository
from app.modules.usuarios.model import usuario
from app.modules.Pedido.repository import PedidoRepository

class DireccionEntregaUnitofWork(UnitOfWork):
    def __init__ (self, session:Session)-> None:
        super().__init__(session)
        self.direcciones = DireccionEntregaRepository(session)
        self.usuarios = usuario(session)
        self.pedidos = PedidoRepository(session)          
        