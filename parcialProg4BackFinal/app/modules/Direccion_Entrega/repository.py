from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.Direccion_Entrega.models import Direccion



class DireccionEntregaRepository(BaseRepository[Direccion]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Direccion)

    def get_active(self, offset: int = 0, limit: int = 20) -> list[Direccion]:
        statement = (
            select(Direccion)
            .where(Direccion.is_active == True)
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.exec(statement).all()) 