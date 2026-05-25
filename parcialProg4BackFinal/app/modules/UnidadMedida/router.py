from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.modules.UnidadMedida.service import UnidadMedidaService
from app.modules.UnidadMedida.schemas import (
    UnidadMedidaCreate, UnidadMedidaUpdate,
    UnidadMedidaPublic, UnidadMedidaList
)

router = APIRouter()


def get_unidad_service(session: Session = Depends(get_session)) -> UnidadMedidaService:
    return UnidadMedidaService(session)


@router.get(
    "/",
    response_model=UnidadMedidaList,
    summary="Listar unidades de medida (paginado)",
)
def list_unidades(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    svc: UnidadMedidaService = Depends(get_unidad_service),
) -> UnidadMedidaList:
    return svc.get_all(offset=offset, limit=limit)


@router.get(
    "/{unidad_id}",
    response_model=UnidadMedidaPublic,
    summary="Obtener unidad de medida por ID",
)
def get_unidad(
    unidad_id: int,
    svc: UnidadMedidaService = Depends(get_unidad_service),
) -> UnidadMedidaPublic:
    return svc.get_by_id(unidad_id)


@router.post(
    "/",
    response_model=UnidadMedidaPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear unidad de medida (solo ADMIN)",
)
def create_unidad(
    data: UnidadMedidaCreate,
    svc: UnidadMedidaService = Depends(get_unidad_service),
) -> UnidadMedidaPublic:
    return svc.create(data)


@router.patch(
    "/{unidad_id}",
    response_model=UnidadMedidaPublic,
    summary="Actualizar unidad de medida (solo ADMIN)",
)
def update_unidad(
    unidad_id: int,
    data: UnidadMedidaUpdate,
    svc: UnidadMedidaService = Depends(get_unidad_service),
) -> UnidadMedidaPublic:
    return svc.update(unidad_id, data)


@router.delete(
    "/{unidad_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar unidad de medida (solo ADMIN)",
)
def delete_unidad(
    unidad_id: int,
    svc: UnidadMedidaService = Depends(get_unidad_service),
) -> None:
    svc.delete(unidad_id)