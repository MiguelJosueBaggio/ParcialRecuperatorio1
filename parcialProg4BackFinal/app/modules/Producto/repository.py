from typing import Optional
from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.Producto.models import Producto
from app.modules.Ingrediente.models import Ingrediente, productoIngredienteLink


class ProductoRepository(BaseRepository[Producto]):
    ##Inicializo el repositorio 

    def __init__(self, session:Session)-> None:
              super().__init__(session, Producto)

    def get_by_ingrediente(self, ingrediente_id: int) -> list[Producto]:
         statement = (
        select(Producto)
        .join(productoIngredienteLink)
        .where(productoIngredienteLink.ingrediente_id == ingrediente_id)
    )
         return list(self.session.exec(statement).all())


    def get_active(self, offset: int = 0, limit: int = 20, categoria_id: Optional[int] = None) -> list[Producto]:
         statement = select(Producto).where(Producto.is_active == True)
         if categoria_id is not None:
              statement = statement.where(Producto.categoria_id == categoria_id)
         statement = statement.offset(offset).limit(limit)
         return list(self.session.exec(statement).all())