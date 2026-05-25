from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.UnidadMedida.models import UnidadMedida


class UnidadMedidaRepository(BaseRepository[UnidadMedida]):

    def __init__(self, session: Session) -> None:
        super().__init__(session, UnidadMedida)

    def get_by_nombre(self, nombre: str) -> UnidadMedida | None:
        return self.session.exec(
            select(UnidadMedida).where(UnidadMedida.nombre == nombre)
        ).first()

    def get_by_simbolo(self, simbolo: str) -> UnidadMedida | None:
        return self.session.exec(
            select(UnidadMedida).where(UnidadMedida.simbolo == simbolo)
        ).first()

    def get_by_tipo(self, tipo: str) -> list[UnidadMedida]:
        return list(self.session.exec(
            select(UnidadMedida).where(UnidadMedida.tipo == tipo)
        ).all())

    def get_all_paginado(self, offset: int = 0, limit: int = 20) -> list[UnidadMedida]:
        return list(self.session.exec(
            select(UnidadMedida).offset(offset).limit(limit)
        ).all())

    def count_all(self) -> int:
        from sqlalchemy import func
        from sqlmodel import select
        return self.session.exec(
            select(func.count()).select_from(UnidadMedida)
        ).one()