from datetime import date
from decimal import Decimal
from sqlmodel import select
from sqlalchemy import func


from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.Producto.models import Producto
from app.modules.DetallePedido.models import DetallePedido
from app.modules.Pedido.models import Pedido    

class PedidoRepository(BaseRepository[Pedido]):
    ##Inicializo el repositorio 

    def __init__(self, session:Session)-> None:
              super().__init__(session, Pedido)

    def get_active(self, offset: int = 0, limit: int = 20) -> list[Pedido]:
        statement = (
        select(Pedido)
        .where(Pedido.is_active == True)
        .offset(offset)
        .limit(limit)
    )
        return list(self.session.exec(statement).all())
    
    def get_pedidos_by_estado(self, estado_codigo: str, offset: int = 0, limit: int = 20) -> list[Pedido]:
        statement = (
        select(Pedido)
        .where(Pedido.estado_codigo == estado_codigo)
        .offset(offset)
        .limit(limit)
    )
        return self.session.exec(statement).all()
    
   ##dashbaoard, obtener la cantidad de pedidos por estado
    def count_pedidos_by_estado(self) -> dict:
        statement = (
        select(
            Pedido.estado_codigo.label("estado"),
            func.count(Pedido.id).label("cantidad")
        )
        .group_by(Pedido.estado_codigo)
    )

        result = self.session.exec(statement).mappings().all()

        return {r["estado"]: r["cantidad"] for r in result}
    
    def obtener_total_ingresos(self, offset: int = 0, limit: int = 20) -> float:
        statement = (
        select(Pedido)
        .where(Pedido.is_active == True)
        .where(Pedido.estado_codigo == "ENTREGADO") 
        .offset(offset)
        .limit(limit)
    )
        return sum(p.total for p in self.session.exec(statement).all())
    
    def obtener_promedio_ingresos(self, offset: int = 0, limit: int = 20) -> float:
        statement = (
        select(Pedido)
        .where(Pedido.is_active == True)
        .where(Pedido.estado_codigo == "ENTREGADO") 
        .offset(offset)
        .limit(limit)
    )
        pedidos_entregados = self.session.exec(statement).all()
        if pedidos_entregados:
            return sum(p.total for p in pedidos_entregados) / len(pedidos_entregados)
        return 0.0  
    
    def get_ventas_periodo(self,desde: date, hasta: date, agrupacion: str): #USADOS
         periodo=func.date_trunc(agrupacion, Pedido.created_at).label("periodo")
         statement = (
        select(
            periodo,
            func.sum(Pedido.total).label("total_ventas"),
            func.count(Pedido.id).label("cantidad_pedidos"),
        )
        .where(Pedido.created_at.between(desde, hasta))
        .where(Pedido.estado_codigo != "CANCELADO")
        .group_by(periodo)
        .order_by(periodo)
    )

         return self.session.exec(statement).all()
    
    def top_productos_mas_vendidos(self, limit: int = 10): #USADOS
        statement = (
            select(
                DetallePedido.producto_id,
                func.sum(DetallePedido.cantidad).label("total_vendido"),
            )
            .join(Pedido, Pedido.id == DetallePedido.pedido_id)
            
            .where(Pedido.estado_codigo != "CANCELADO")
            .group_by(DetallePedido.producto_id)
            .order_by(func.sum(DetallePedido.cantidad).desc())
            .limit(limit)
        )
        return self.session.exec(statement).all()
    
    def get_pedidos_por_forma_pago(self):
        statement = (
            select(
                Pedido.forma_pago_codigo,
                func.count(Pedido.id).label("total_pedidos"),
                #func.sum(Pedido.total).label("total_ventas"),
                #func.avg(Pedido.total).label("promedio_ventas"),
            )
            .group_by(Pedido.forma_pago_codigo) 
        )
        return self.session.exec(statement).all()
    #kpis
    def ventas_hoy(self):
        today = date.today()
        statement = (
            select(func.sum(Pedido.total).label("total_ventas"))
            .where(func.date(Pedido.created_at) == today)
            .where(Pedido.estado_codigo != "CANCELADO")
        )
        result = self.session.exec(statement).one()
        return result or 0.0 
    def ticket_promedio(self):
        statement = (
            select(func.avg(Pedido.total).label("ticket_promedio"))
            .where(Pedido.estado_codigo != "CANCELADO")
        )
        result = self.session.exec(statement).one()
        return float(result or 0) 
    def pedidos_activos(self):
        statement = (
            select(func.count(Pedido.id).label("pedidos_activos"))
            .where(Pedido.estado_codigo != "CANCELADO")
        )
        result = self.session.exec(statement).one()
        return result.pedidos_activos if result.pedidos_activos is not None else 0
    def mes_actual_ventas(self):
        today = date.today()
        first_day_of_month = today.replace(day=1)

        statement = (
        select(func.sum(Pedido.total))
        .where(Pedido.created_at >= first_day_of_month)
        .where(Pedido.estado_codigo != "CANCELADO")
    )

        result = self.session.exec(statement).one_or_none()

        return result or 0.0