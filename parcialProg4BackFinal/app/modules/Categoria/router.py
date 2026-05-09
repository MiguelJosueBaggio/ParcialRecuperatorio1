from fastapi import APIRouter, Depends,Query,status
from sqlmodel import Session
from app.core.database import get_session
from app.modules.Categoria.service import CategoriaService
from app.modules.Categoria.schemas import CategoriaCreate,CategoriaUpDate,CategoriaPublic,CategoriaList   

router = APIRouter()



def get_categoria_service(session: Session = Depends(get_session)) -> CategoriaService:
    """Factory de dependencia: inyecta el servicio con su Session."""
    return CategoriaService(session)


# ── Endpoints ─────────────────────────────────────────────────────────────────
##CREAR cat
@router.post(
    "/",
    response_model=CategoriaPublic,
    status_code=status.HTTP_201_CREATED,
    summary="crear  un categoria",
)
def create_ingrediente(
    data: CategoriaCreate,
    svc: CategoriaService = Depends(get_categoria_service),
) -> CategoriaPublic:
    """Router delega al servicio — sin lógica de negocio aquí."""
    return svc.create(data)

#OBTENER categoria
@router.get(
    "/",
    response_model=CategoriaList,
    summary="Listar categoria activos (paginado)",
)
def list_categorias(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    svc: CategoriaService = Depends(get_categoria_service),
) -> CategoriaService:
    return svc.get_all(offset=offset, limit=limit)

##OBTENER categoria POR ID
@router.get(
    "/{categoria_id}",
    response_model=CategoriaPublic,
    summary="Obtener cat por ID",
)
def get_categoria(
    categoria_id: int,
    svc: CategoriaService = Depends(get_categoria_service),
) -> CategoriaPublic:
    return svc.get_by_id(categoria_id)

##get subcatgoriaby_id

@router.get(
    "/subcategoria{categoria_id}",
    response_model=CategoriaPublic,
    summary="Obtener subcat por ID",
)
def get_categoria(
    categoria_id: int,
    svc: CategoriaService = Depends(get_categoria_service),
) -> CategoriaPublic:
    return svc.get_by_id(categoria_id)




@router.patch(
    "/{categoria_id}",
    response_model=CategoriaPublic,
    summary="Actualización parcial de Catebgoria",
)
def update_ingrediente(
    categoria_id: int,
    data: CategoriaUpDate,
    svc: CategoriaService = Depends(get_categoria_service),
) -> CategoriaPublic:
    return svc.update(categoria_id, data)


@router.delete(
    "/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete de categoria",
)
def delete_ingrediente(
    categoria_id: int,
    svc: CategoriaService = Depends(get_categoria_service),
) -> None:
    svc.soft_delete(categoria_id)
