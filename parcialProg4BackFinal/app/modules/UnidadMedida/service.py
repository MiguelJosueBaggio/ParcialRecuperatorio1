from sqlmodel import Session

from app.modules.UnidadMedida.schemas import UnidadMedidaPublic, UnidadMedidaList
from app.modules.UnidadMedida.unit_of_work import UnidadMedidaUnitOfWork


class UnidadMedidaService:

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_all(self, offset: int = 0, limit: int = 20) -> UnidadMedidaList:
        with UnidadMedidaUnitOfWork(self._session) as uow:
            unidades = uow.unidad_medida_repository.get_all_paginado(offset=offset, limit=limit)
            total = uow.unidad_medida_repository.count_all()

            result = UnidadMedidaList(
                data=[UnidadMedidaPublic.model_validate(u) for u in unidades],
                total=total,
            )

        return result

    def get_by_tipo(self, tipo: str) -> list[UnidadMedidaPublic]:
        with UnidadMedidaUnitOfWork(self._session) as uow:
            unidades = uow.unidad_medida_repository.get_by_tipo(tipo)
            return [UnidadMedidaPublic.model_validate(u) for u in unidades]