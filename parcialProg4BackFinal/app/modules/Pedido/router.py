from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session        
from app.core.database import get_session
from app.modules.Pedido.service import PedidoService        
from app.modules.Pedido.schemas import PedidoCreate, PedidoPublic, PedidoList, PedidoUpdate 
router = APIRouter()
def get_pedido_service(session: Session = Depends(get_session)) -> PedidoService:
    """Factory de dependencia: inyecta el servicio con su Session."""
    return PedidoService(session)       




@router.post(
    "/",                
    response_model=PedidoPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo pedido",
)
def create_pedido(
    data: PedidoCreate,
    svc: PedidoService = Depends(get_pedido_service),
) -> PedidoPublic:
    """Router delega al servicio — sin lógica de negocio aquí."""
    return svc.create(data) 





@router.get(
    "/",        
    response_model=PedidoList,
    summary="Listar pedidos activos (paginado)",
)
def list_pedidos(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    svc: PedidoService = Depends(get_pedido_service),
) -> PedidoList:
    return svc.get_all(offset=offset, limit=limit)  





@router.get("/estados", response_model=list[str], summary="Listar estados de pedidos")
def listar_estados(
    svc: PedidoService = Depends(get_pedido_service),
):
    return svc.listar_estados()




@router.get(
    "/{pedido_id}",     
    response_model=PedidoPublic,
    summary="Obtener pedido por ID",
)   
def get_pedido(
    pedido_id: int,
    svc: PedidoService = Depends(get_pedido_service),
) -> PedidoPublic:
    return svc.get_by_id(pedido_id)



@router.patch(
    "/{pedido_id}",     
    response_model=PedidoPublic,
    summary="Actualizar pedido por ID",
)
def update_pedido(
    pedido_id: int,
    data: PedidoUpdate,
    svc: PedidoService = Depends(get_pedido_service),
) -> PedidoPublic:
    return svc.update(pedido_id, data)   




@router.delete(
    "/{pedido_id}",     
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar (soft delete) pedido por ID",
)  
def delete_pedido(
    pedido_id: int,
    svc: PedidoService = Depends(get_pedido_service),
) -> None:
    svc.soft_delete(pedido_id)

        