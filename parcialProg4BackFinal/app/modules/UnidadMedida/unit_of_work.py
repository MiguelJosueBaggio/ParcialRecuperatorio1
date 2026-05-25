from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.UnidadMedida.repository import UnidadMedidaRepository

class UnidadMedidaUnitOfWork(UnitOfWork):

    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.unidad_medida_repository = UnidadMedidaRepository(session)