from fastapi import HTTPException, status
from sqlmodel import Session

from app.modules.Ingrediente.models import Ingrediente, productoIngredienteLink
from app.modules.Estadisticas.schemas import ResumenResponse,VentasPorPeriodoItem,GetPedidosPorEstado,GetPedidosPorFormaPago,GetProductosMasVendidos
from app.modules.Ingrediente.unit_of_work import IngredienteUnitofWork
from app.modules.Pedido.unit_of_work import PedidoUnitofWork
from app.modules.Producto.unit_of_work import ProductoUnitofWork
from datetime import date, datetime

class EstadisticasService:

    ##Inicia servecie
    def __init__(self, session: Session) -> None:
        
        self._session = session

    def ventas_por_periodo(self, desde: str, hasta: str, agrupacion: str) -> list[VentasPorPeriodoItem]:
        desde_date = date.fromisoformat(desde)
        hasta_date = date.fromisoformat(hasta)
        with PedidoUnitofWork(self._session) as uow:
          rows = uow.pedidos.get_ventas_periodo(desde_date, hasta_date, agrupacion)
        return [
            VentasPorPeriodoItem(
                periodo=r.periodo,
                total_ventas=r.total_ventas,
                cantidad_pedidos=r.cantidad_pedidos,
            )
            for r in rows
        ]
    
    def productos_mas_vendidos(self,  limit: int = 10) -> list[GetProductosMasVendidos]:
       
        with PedidoUnitofWork(self._session) as uow:
            rows = uow.pedidos.top_productos_mas_vendidos(limit)    
        return [
            GetProductosMasVendidos(
                producto=r.producto,
                total_ventas=r.total_ventas,
                cantidad_pedidos=r.cantidad_pedidos,        
                promedio_ventas=r.promedio_ventas
            )
            for r in rows
        ]   
    def obtener_pedidos_por_estado(self) -> list[GetPedidosPorEstado]:
        with PedidoUnitofWork(self._session) as uow:
            rows = uow.pedidos.count_pedidos_by_estado() or {}
        return [
            GetPedidosPorEstado(
                estado=estado,
                total_pedidos=count
            )
            for estado, count in rows.items()
        ]       
    
    def obtener_pedidos_por_forma_pago(self) -> list[GetPedidosPorFormaPago]:
        with PedidoUnitofWork(self._session) as uow:
            rows = uow.pedidos.get_pedidos_por_forma_pago() or []  
        return [
            GetPedidosPorFormaPago(
                forma_pago=str(forma_pago),
                total_pedidos=count
            )
            for forma_pago, count in rows
        ]
    def obtener_resumen(self) -> ResumenResponse:
        with PedidoUnitofWork(self._session) as uow:
            estado_counts = uow.pedidos.count_pedidos_by_estado()
            ventas_hoy = uow.pedidos.ventas_hoy()
            ticket_promedio = uow.pedidos.ticket_promedio()
            pedidos_hoy = sum(estado_counts.get(estado, 0) for estado in ["PENDIENTE", "EN_PROCESO", "ENTREGADO"]   )
            mes_actual_ventas = uow.pedidos.mes_actual_ventas()
        return ResumenResponse(
            ventas_hoy=ventas_hoy,
            ticket_promedio=ticket_promedio,
            pedidos_hoy=pedidos_hoy,
            mes_actual_ventas=mes_actual_ventas
        )   
    