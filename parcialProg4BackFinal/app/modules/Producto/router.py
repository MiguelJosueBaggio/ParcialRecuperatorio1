from fastapi import APIRouter, Depends,Query,status
from sqlmodel import Session
from app.core.database import get_session
from app.modules.Producto.service import ProductoService
from app.modules.Producto.schemas import ProductoCreate,ProductoUpdate,ProductoPublic,ProductoList
   

router = APIRouter()


def get_producto_service(session: Session = Depends(get_session)) -> ProductoService:
    """Factory de dependencia: inyecta el servicio con su Session."""
    return ProductoService(session)


# ── Endpoints ─────────────────────────────────────────────────────────────────
##CREAR INGREDIENTE
@router.post(
    "/",
    response_model=ProductoPublic,
    status_code=status.HTTP_201_CREATED,
    summary="crear un producto",
)
def create_ingrediente(
    data: ProductoCreate,
    svc: ProductoService = Depends(get_producto_service),
) -> ProductoPublic:
    """Router delega al servicio — sin lógica de negocio aquí."""
    return svc.create(data)

#OBTENER INGREDIENETES
@router.get(
    "/",
    response_model=ProductoList,
    summary="Listar productos activos (paginado)",
)
def list_ingredientes(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    svc: ProductoService = Depends(get_producto_service),
) -> ProductoList:
    return svc.get_all(offset=offset, limit=limit)

##OBTENER INGREDIENTES POR ID
@router.get(
    "/{producto_id}",
    response_model=ProductoPublic,
    summary="Obtener producto por ID",
)
def get_producto(
    producto_id: int,
    svc: ProductoService= Depends(get_producto_service),
) -> ProductoPublic:
    return svc.get_by_id(producto_id)

##obteneralergenos



#modificar
@router.patch(
    "/{producto_id}",
    response_model=ProductoPublic,
    summary="Actualización parcial de producto",
)
def update_hero(
    producto_id: int,
    data: ProductoUpdate,
    svc: ProductoService = Depends(get_producto_service),
) -> ProductoPublic:
    return svc.update(producto_id, data)


@router.delete(
    "/{producto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete de producto",
)
def delete_ingrediente(
    producto_id: int,
    svc: ProductoService = Depends(get_producto_service),
) -> None:
    svc.soft_delete(producto_id)

