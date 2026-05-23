from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.Producto.models import Producto
from app.modules.DetallePedido import DetallePedido


class DetallePedidoRepository(BaseRepository[DetallePedido]):
    ##Inicializo el repositorio 

    def __init__(self, session:Session)-> None:
              super().__init__(session, DetallePedido)

    def get_active(self, offset: int = 0, limit: int = 20) -> list[DetallePedido]:
        statement = (
        select(DetallePedido)
        .where(DetallePedido.is_active == True)
        .offset(offset)
        .limit(limit)
    )
        return list(self.session.exec(statement).all())
    def obtener_precio_producto(self, producto_id: int) -> float:
        statement = select(Producto).where(Producto.id == producto_id)             ##obtenemos precio del prodocto para suincluirlo en snapshot precio 
        producto = self.session.exec(statement).first()
        if producto:
            return producto.precio
        else:
            raise ValueError(f"Producto con id {producto_id} no encontrado")
        
    def obtener_stock_producto(self, producto_id:int)-> int:
        statement = select(Producto).where(Producto.id == producto_id)             ##obtenemos stock  del prodocto para suincluirlo en snapshot precio 
        producto = self.session.exec(statement).first()
        if producto:
            return producto.stock_cantidad
        else:
            raise ValueError(f"Producto con id {producto_id} no encontrado")
         