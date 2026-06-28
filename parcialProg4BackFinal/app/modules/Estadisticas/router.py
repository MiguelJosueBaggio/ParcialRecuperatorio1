from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session        
from app.core.database import get_session
from app.modules.Estadisticas.service import EstadisticasService        
from app.modules.Estadisticas.schemas import ResumenResponse,VentasPorPeriodoItem,GetPedidosPorEstado,GetPedidosPorFormaPago,GetProductosMasVendidos

router = APIRouter()
def get_estadisticas_service(session: Session = Depends(get_session)) -> EstadisticasService:
    """Factory de dependencia: inyecta el servicio con su Session."""
    return EstadisticasService(session)    

@router.get(
    "/resumen/",
    response_model=ResumenResponse,
    summary="Obtener resumen de estadísticas",
)   
def get_resumen(
    svc: EstadisticasService = Depends(get_estadisticas_service),
) -> ResumenResponse:
    """Router delega al servicio — sin lógica de negocio aquí."""
    return svc.obtener_resumen()            

@router.get(
    "/ventas-por-periodo/",
    response_model=list[VentasPorPeriodoItem],
    summary="Obtener ventas por periodo",   
)
def get_ventas_por_periodo( 
    desde: str = Query(..., description="Fecha de inicio en formato YYYY-MM-DD"),
    hasta: str = Query(..., description="Fecha de fin en formato YYYY-MM-DD"),
    agrupacion: str = Query(..., description="Agrupación de los datos (day, week, month, year)"),
    svc: EstadisticasService = Depends(get_estadisticas_service),
) -> list[VentasPorPeriodoItem]:
    """Router delega al servicio — sin lógica de negocio aquí."""
    return svc.ventas_por_periodo(desde=desde, hasta=hasta, agrupacion=agrupacion)      

@router.get(
    "/productos-mas-vendidos/",
    response_model=list[GetProductosMasVendidos],
    summary="Obtener productos más vendidos",
)
def get_productos_mas_vendidos( 
    
    limit: int = Query(10, description="Cantidad máxima de productos a retornar"),
    svc: EstadisticasService = Depends(get_estadisticas_service),
) -> list[GetProductosMasVendidos]:
    """Router delega al servicio — sin lógica de negocio aquí."""
    return svc.productos_mas_vendidos( limit=limit)        


@router.get(
    "/pedidos-por-estado/",
    response_model=list[GetPedidosPorEstado],
    summary="Obtener cantidad de pedidos por estado",
)  
def get_pedidos_por_estado(
    svc: EstadisticasService = Depends(get_estadisticas_service),
) -> list[GetPedidosPorEstado]:
    """Router delega al servicio — sin lógica de negocio aquí."""
    return svc.obtener_pedidos_por_estado() 

@router.get(
    "/pedidos-por-forma-pago/",
    response_model=list[GetPedidosPorFormaPago],
    summary="Obtener cantidad de pedidos por forma de pago",
) 
def get_pedidos_por_forma_pago(
    svc: EstadisticasService = Depends(get_estadisticas_service),
) -> list[GetPedidosPorFormaPago]:
    """Router delega al servicio — sin lógica de negocio aquí."""
    return svc.obtener_pedidos_por_forma_pago() 
