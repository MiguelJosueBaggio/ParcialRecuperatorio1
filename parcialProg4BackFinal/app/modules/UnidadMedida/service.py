from fastapi import HTTPException, status
from sqlmodel import Session

from app.modules.UnidadMedida.models import UnidadMedida
from app.modules.UnidadMedida.schemas import (
    UnidadMedidaCreate, UnidadMedidaUpdate,
    UnidadMedidaPublic, UnidadMedidaList
)
from app.modules.UnidadMedida.unit_of_work import UnidadMedidaUnitOfWork


class UnidadMedidaService:

    def __init__(self, session: Session) -> None:
        self._session = session

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_or_404(self, uow: UnidadMedidaUnitOfWork, unidad_id: int) -> UnidadMedida:
        unidad = uow.unidades.get_by_id(unidad_id)
        if not unidad:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unidad de medida con id={unidad_id} no encontrada",
            )
        return unidad

    def _assert_nombre_unico(self, uow: UnidadMedidaUnitOfWork, nombre: str) -> None:
        if uow.unidades.get_by_nombre(nombre):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe una unidad de medida con nombre '{nombre}'",
            )

    def _assert_simbolo_unico(self, uow: UnidadMedidaUnitOfWork, simbolo: str) -> None:
        if uow.unidades.get_by_simbolo(simbolo):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe una unidad de medida con símbolo '{simbolo}'",
            )

    # ── Operaciones ───────────────────────────────────────────────────────────

    def get_all(self, offset: int = 0, limit: int = 20) -> UnidadMedidaList:
        with UnidadMedidaUnitOfWork(self._session) as uow:
            unidades = uow.unidades.get_all_paginado(offset=offset, limit=limit)
            total = uow.unidades.count_all()
            return UnidadMedidaList(
                data=[UnidadMedidaPublic.model_validate(u) for u in unidades],
                total=total,
            )

    def get_by_id(self, unidad_id: int) -> UnidadMedidaPublic:
        with UnidadMedidaUnitOfWork(self._session) as uow:
            unidad = self._get_or_404(uow, unidad_id)
            return UnidadMedidaPublic.model_validate(unidad)

    def create(self, data: UnidadMedidaCreate) -> UnidadMedidaPublic:
        with UnidadMedidaUnitOfWork(self._session) as uow:
            self._assert_nombre_unico(uow, data.nombre)
            self._assert_simbolo_unico(uow, data.simbolo)

            unidad = UnidadMedida.model_validate(data)
            uow.unidades.add(unidad)
            return UnidadMedidaPublic.model_validate(unidad)

    def update(self, unidad_id: int, data: UnidadMedidaUpdate) -> UnidadMedidaPublic:
        with UnidadMedidaUnitOfWork(self._session) as uow:
            unidad = self._get_or_404(uow, unidad_id)

            if data.nombre is not None and data.nombre != unidad.nombre:
                self._assert_nombre_unico(uow, data.nombre)

            if data.simbolo is not None and data.simbolo != unidad.simbolo:
                self._assert_simbolo_unico(uow, data.simbolo)

            patch = data.model_dump(exclude_unset=True)
            for field, value in patch.items():
                setattr(unidad, field, value)

            uow.unidades.add(unidad)
            return UnidadMedidaPublic.model_validate(unidad)

    def delete(self, unidad_id: int) -> None:
        """
        UnidadMedida es un catálogo — usa delete físico ya que no tiene deleted_at.
        En producción se debería validar que no esté en uso antes de eliminar.
        """
        with UnidadMedidaUnitOfWork(self._session) as uow:
            unidad = self._get_or_404(uow, unidad_id)
            uow.unidades.delete(unidad)