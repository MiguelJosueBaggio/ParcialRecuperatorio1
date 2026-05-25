from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.usuarios.repository import UsuarioRepository   
from app.modules.Rol.repository import RolRepository    
from app.modules.Direccion_Entrega.repository import DireccionEntregaRepository

class UsuarioUnitofWork(UnitOfWork):
    def __init__ (self, session:Session)-> None:
        super().__init__(session)
        self.usuarios= UsuarioRepository(session)
        self.rols = RolRepository(session)
        self.direcciones = DireccionEntregaRepository(session)
        