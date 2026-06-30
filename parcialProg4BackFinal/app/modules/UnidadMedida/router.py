from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.database import get_session
from app.modules.UnidadMedida.service import UnidadMedidaService
from app.modules.UnidadMedida.schemas import UnidadMedidaPublic, UnidadMedidaList

router = APIRouter()


def get_unidad_medida_service(session: Session = Depends(get_session)) -> UnidadMedidaService:
    """Factory de dependencia: inyecta el servicio con su Session."""
    return UnidadMedidaService(session)


@router.get(
    "/",
    response_model=UnidadMedidaList,
    summary="Listar catálogo de unidades de medida (paginado)",
)
def list_unidades_medida(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    svc: UnidadMedidaService = Depends(get_unidad_medida_service),
) -> UnidadMedidaList:
    return svc.get_all(offset=offset, limit=limit)


@router.get(
    "/tipo/{tipo}",
    response_model=list[UnidadMedidaPublic],
    summary="Listar unidades de medida por tipo (masa, volumen, unidad, area)",
)
def list_unidades_medida_por_tipo(
    tipo: str,
    svc: UnidadMedidaService = Depends(get_unidad_medida_service),
) -> list[UnidadMedidaPublic]:
    return svc.get_by_tipo(tipo)