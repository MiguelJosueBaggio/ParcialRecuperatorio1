from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.Ingrediente.models import Ingrediente, productoIngredienteLink

class IngredienteRepository(BaseRepository[Ingrediente]):
    ##Inicializo el repositorio 
    def __init__(self, session:Session)-> None:
              super().__init__(session, Ingrediente)

           ## obtener lista de alergenos   
    def get_alergenos(self, offset: int=0, limit: int= 10)  ->list[Ingrediente]:
           
             return list(
            self.session.exec(
                select(Ingrediente)
                .where(Ingrediente.es_alergeno== True) 
                .where(Ingrediente.is_active == True)  
                .offset(offset)
                .limit(limit)
            ).all()
        )
            
    def get_by_producto(self, producto_id: int) -> list[Ingrediente]:
         statement = (
        select(Ingrediente)
        .join(productoIngredienteLink)
        .where(productoIngredienteLink.producto_id == producto_id)
    )
         return list(self.session.exec(statement).all())
    def get_active(self, offset: int = 0, limit: int = 20) -> list[Ingrediente]:
        statement = (
        select(Ingrediente)
        .where(Ingrediente.is_active == True)
        .offset(offset)
        .limit(limit)
    )
        return list(self.session.exec(statement).all())
    
    