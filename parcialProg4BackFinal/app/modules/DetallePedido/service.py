'''from fastapi import HTTPException, status
from sqlmodel import Session

from app.modules.DetallePedido.models import DetallePedido
from app.modules.DetallePedido.schema import DetallePedidoCreate, DetallePedidoPublic, DetallePedidoUpdate,DetallePedidoList
from app.modules.DetallePedido.unit_of_work import DetallePedidoUnitofWork

class DetallePedidoService:

    ##Inicia servecie
    def __init__(self, session: Session) -> None:
        
        self._session = session

##obtenemos un producto por su id sino retruna error 404
    def _get_or_404(self, uow: DetallePedidoUnitofWork, detalle_pedido_id: int) -> DetallePedido:
        
       
        detallePedido = uow.detalle_pedidos.get_by_id(detalle_pedido_id)
        if not detallePedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"detalle_id con id={detalle_pedido_id} no encontrado",
            )
        return detallePedido
   
    ###Obtenemos los activos
    def get_all(self, offset: int = 0, limit: int = 10) -> DetallePedidoList:
        with DetallePedidoUnitofWork(self._session) as uow:
            detalle_pedidos = uow.detalle_pedidos.get_active(  ####REVISAR
              offset=offset,
               limit=limit
        )

        total = uow.detalle_pedidos.count()

        result = DetallePedidoList(
            data=[
                DetallePedidoPublic.model_validate(i)
                for i in detalle_pedidos
            ],
            total=total,
        )

        return result
        ##obtener ingrediente del produto segun su id
  
    def get_producto_or_404(self,uow:DetallePedidoUnitofWork, producto_id:int):
        
        producto = uow.productos.get_by_id(producto_id)
        if not producto:
            raise HTTPException(
                status_code=404,
                detail=f"el produto con id={producto_id} no encontrado"
            )
        return producto


##Obten buscar por id

    def get_by_id(self, detalle_pedido_id: int) -> DetallePedidoPublic:
        
        with DetallePedidoUnitofWork(self._session) as uow:
            detalle_pedido = self._get_or_404(uow, detalle_pedido_id)
            result = DetallePedidoPublic.model_validate(detalle_pedido)

        return result    
   
    def __calcular_subtotal(self,data:DetallePedidoCreate)->float:

        with DetallePedidoUnitofWork(self._session) as uow:
          sutotal=data.cantidad*data.precio_snapshot
        return sutotal


 
##crea producto

    def create(self, data: ) -> ProductoPublic:
        
       
        with ProductoUnitofWork(self._session) as uow:
           
            self.get_categoria_or_404(uow, data.categoria_id)

            producto = Producto.model_validate(data)
            for ingrediente_id in data.ingrediente_ids: ##recoerre los ingredientes agregados
                 ingrediente= self.get_ingrediente_or_404(uow,ingrediente_id)##si esta presemnete el ingrediente se guarga en ingrediente
                 producto.ingredientes.append(ingrediente) ##guardamos el ingredeinte en ela lista que ira  a la base de datos

           

            
           
            
            uow.productos.add(producto)

            
            result = ProductoPublic.model_validate(producto)

        return result
    

    ###Modificador
    
    def update(self, producto_id: int, data: ProductoUpdate) -> ProductoPublic:
      with ProductoUnitofWork(self._session) as uow:
        producto = self._get_or_404(uow, producto_id)

        # 🔹 Relación muchos a muchos: ingredientes
        if data.ingrediente_ids is not None:
            ingredientes = []

            for ingrediente_id in data.ingrediente_ids:
                ingrediente = self._get_ingrediente_or_404(uow, ingrediente_id)
                ingredientes.append(ingrediente)

            producto.ingredientes.clear()
            producto.ingredientes.extend(ingredientes)

        # 🔹 Categoría
        if data.categoria_id is not None:
            categoria = self._get_categoria_or_404(uow, data.categoria_id)
            producto.categoria = categoria

        # 🔹 Campos simples (excluyendo relaciones)
        patch = data.model_dump(
            exclude_unset=True,
            exclude={"ingrediente_ids", "categoria_id"}
        )

        for field, value in patch.items():
            setattr(producto, field, value)

        uow.productos.add(producto)

      return ProductoPublic.model_validate(producto)


    ##eliminar
    def soft_delete(self, producto_id: int) -> None:
        
        with ProductoUnitofWork(self._session) as uow:
            producto= self.get_or_404(uow, producto_id)
            producto.is_active = False
            uow.productos.add(producto)'''