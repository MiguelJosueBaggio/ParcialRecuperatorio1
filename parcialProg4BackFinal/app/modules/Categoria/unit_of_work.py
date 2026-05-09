from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork

from app.modules.Producto.repository import ProductoRepository
from app.modules.Categoria.repository import CategoriaRepository

class CategoriaUnitofWork(UnitOfWork):
    def __init__ (self, session:Session)-> None:
        super().__init__(session)
        
        self.productos = ProductoRepository(session)
        self.categorias = CategoriaRepository(session)
        