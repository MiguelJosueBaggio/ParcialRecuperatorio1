from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.Categoria.models import Categoria
from app.modules.Producto.models import Producto
class CategoriaRepository(BaseRepository[Categoria]):
    ##Inicializo el repositorio 
    def __init__(self, session:Session)-> None:
              super().__init__(session, Categoria)


    def get_by_name(self, nombre: str) -> Categoria | None:
        
        return self.session.exec(
            select(Categoria).where(Categoria.nombre == nombre)
        ).first()
    
    def get_active(self, offset: int = 0, limit: int = 20) -> list[Categoria]:
        statement = (
        select(Categoria)
        .where(Categoria.is_active == True)
        .offset(offset)
        .limit(limit)
    )
        return list(self.session.exec(statement).all())