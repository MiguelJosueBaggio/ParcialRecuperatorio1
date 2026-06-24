from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.Producto.models import Producto
from app.modules.Ingrediente.models import Ingrediente, productoIngredienteLink
from app.modules.DetallePedido.models import DetallePedido


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
            return producto.precio_base
        else:
            raise ValueError(f"Producto con id {producto_id} no encontrado")

    def obtener_nombre_producto(self, producto_id: int) -> str:
        statement = select(Producto).where(Producto.id == producto_id)             ##obtenemos nombre del prodocto para suincluirlo en snapshot nombre 
        producto = self.session.exec(statement).first()
        if producto:
            return producto.nombre
        else:
            raise ValueError(f"Producto con id {producto_id} no encontrado")        

    def obtener_stock_producto(self, producto_id:int)-> int:
        statement = select(Producto).where(Producto.id == producto_id)             ##obtenemos stock  del prodocto para suincluirlo en snapshot precio 
        producto = self.session.exec(statement).first()
        if producto:
            return producto.stock_cantidad
        else:
            raise ValueError(f"Producto con id {producto_id} no encontrado")
    def obtener_cantidad(self, detalle_pedido_id: int) -> int:
        statement = select(DetallePedido).where(DetallePedido.id == detalle_pedido_id)
        detalle = self.session.exec(statement).first()
        if detalle:
           return detalle.cantidad
        raise ValueError(f"DetallePedido con id {detalle_pedido_id} no encontrado")
    def obtener_stock_ingrediente(self,ingrediente_id)->int:
        statiment = select(Ingrediente).where(Ingrediente.id == ingrediente_id)             ##obtenemos stock  del ingredeiente para suincluirlo en snapshot precio 
        ingrediente = self.session.exec(statiment).first()
        if ingrediente:
            return ingrediente.stock_cantidad
        else:
            raise ValueError(f"Ingrediente con id {ingrediente_id} no encontrado")
        
    def is_ingrediente_removible(self, ingrediente_id: int) -> bool:
        statiment = select(Ingrediente).where(Ingrediente.id == ingrediente_id)             ##obtenemos si el ingrediente es removible para permitir su eliminacion en el detalle pedido
        ingrediente = self.session.exec(statiment).first()
        if ingrediente:
            return ingrediente.es_removible
        else:
            raise ValueError(f"Ingrediente con id {ingrediente_id} no encontrado")
    
    def cantidad_ingrediente_producto( self,ingrediente_id: int, producto_id: int) -> float:

        statement = select(productoIngredienteLink).where(
         productoIngredienteLink.ingrediente_id == ingrediente_id,
         productoIngredienteLink.producto_id == producto_id
    )

        link = self.session.exec(statement).first()

        if not link:
          raise ValueError(
            f"Ingrediente con id {ingrediente_id} no asociado al producto con id {producto_id}"
        )

        return float(link.cantidad)