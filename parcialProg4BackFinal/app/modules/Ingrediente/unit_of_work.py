from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.Ingrediente.repository import IngredienteRepository
from app.modules.Producto.repository import ProductoRepository

class IngredienteUnitofWork(UnitOfWork):
    def __init__ (self, session:Session)-> None:
        super().__init__(session)
        self.ingredientes= IngredienteRepository(session)
        self.productos = ProductoRepository(session)
        