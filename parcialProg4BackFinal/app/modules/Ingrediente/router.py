from fastapi import APIRouter, Depends,Query,status
from sqlmodel import Session
from app.core.database import get_session
from app.modules.Ingrediente.service import IngredienteService
from app.modules.Ingrediente.schemas import IngredienteCreate,IngredienteUpsate,IngredientePublic,IngredienteList,ProductoIngredienteCreate,ProductoIngredienteUpdate,ProductoIngredientePublic   
   

router = APIRouter()


def get_ingrediente_service(session: Session = Depends(get_session)) -> IngredienteService:
    """Factory de dependencia: inyecta el servicio con su Session."""
    return IngredienteService(session)


# ── Endpoints ─────────────────────────────────────────────────────────────────
##CREAR INGREDIENTE
@router.post(
    "/",
    response_model=IngredientePublic,
    status_code=status.HTTP_201_CREATED,
    summary="crear un ingrediente",
)
def create_ingrediente(
    data: IngredienteCreate,
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> IngredientePublic:
    """Router delega al servicio — sin lógica de negocio aquí."""
    return svc.create(data)


@router.post(
    "/producto-ingrediente",
    response_model=ProductoIngredientePublic,
    status_code=status.HTTP_201_CREATED,
    summary="asociar ingrediente a producto",
)
def create_producto_ingrediente(
    data: ProductoIngredienteCreate,
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> ProductoIngredientePublic:
    """Router delega al servicio — sin lógica de negocio aquí."""
    return svc.create_producto_ingrediente(data)    

#OBTENER INGREDIENETES
@router.get(
    "/",
    response_model=IngredienteList,
    summary="Listar ingredientes activos (paginado)",
)
def list_ingredientes(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> IngredienteList:
    return svc.get_all(offset=offset, limit=limit)


@router.get(
    "/alergenos",
    response_model=IngredienteList,
    summary="Listar ingredientes alergicos (paginado)",
)
def list_ingredientes_alegenos(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> IngredienteList:
    return svc.get_alergenos(offset=offset, limit=limit)
##OBTENER INGREDIENTES POR ID
@router.get(
    "/{ingrediente_id}",
    response_model=IngredientePublic,
    summary="Obtener ingrediente por ID",
)
def get_ingrediente(
    ingrediente_id: int,
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> IngredientePublic:
    return svc.get_by_id(ingrediente_id)


##obteneralergenos


@router.patch(
    "/{ingrediente_id}",
    response_model=IngredientePublic,
    summary="Actualización parcial de Ingrediente",
)
def update_ingrediente(
    ingrediente_id: int,
    data: IngredienteUpsate,
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> IngredientePublic:
    return svc.update(ingrediente_id, data)


@router.delete(
    "/{ingrediente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete de héroe",
)
def delete_ingrediente(
    ingrediente_id: int,
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> None:
    svc.soft_delete(ingrediente_id)
