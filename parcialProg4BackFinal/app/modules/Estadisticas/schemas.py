from typing import Optional, List

from sqlmodel import SQLModel,Field
from decimal import Decimal
from datetime import date, datetime 

class ResumenResponse(SQLModel):
    ventas_hoy: Decimal
    ticket_promedio: Decimal
    pedidos_hoy: int
    mes_actual_ventas: Decimal

class VentasPorPeriodoItem(SQLModel):
    periodo: date
    total_ventas: Decimal
    cantidad_pedidos: int
    promedio_ventas: Decimal | None = None

class GetPedidosPorEstado(SQLModel):
    estado: str
    total_pedidos: int
    #total_ventas: Decimal
   # promedio_ventas: Decimal    

class GetPedidosPorFormaPago(SQLModel): 
    forma_pago: str
    #total_ventas: Decimal
    total_pedidos: int
    #promedio_ventas: Decimal

class GetProductosMasVendidos(SQLModel):
    producto: str
   
    cantidad_pedidos: int
    