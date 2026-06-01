from sqlmodel import Session, select, func
from app.core.repository import BaseRepository
from app.modules.FormaPago.models import FormaPago  
from app.modules.Pedido.models import Pedido
class FormaPagoRepository(BaseRepository[FormaPago]):
    ##Inicializo el repositorio 
    def __init__(self, session:Session)-> None:
              super().__init__(session, FormaPago)

    def get_habilitados(self, offset: int = 0, limit: int = 20) -> list[FormaPago]:
         statement = (
        select(FormaPago)
        .where(FormaPago.habilitado == True)
        .offset(offset)
        .limit(limit)
    )
         return list(self.session.exec(statement).all())
    
    def count_habilitados(self):
     stmt = (
        select(func.count())
        .select_from(self.model)
        .where(self.model.habilitado == True)
    )

     return self.session.exec(stmt).one()