from fastapi import HTTPException, status
from sqlmodel import Session
from decimal import Decimal
from app.modules.Pedido.models import Pedido
from app.modules.DetallePedido.models import DetallePedido
from app.modules.HistorialPedido.models import HistorialEstadoPedido

from app.modules.Pedido.schemas import PedidoCreate, PedidoPublic, PedidoUpdate, PedidoList, DetallePedidoCreate, DetallePedidoPublic,PedidoEstadoUpdate
from app.modules.Pedido.unit_of_work import PedidoUnitofWork
from app.modules.DetallePedido.unit_of_work import DetallePedidoUnitofWork
from app.modules.EstadoPedido.unit_of_work import EstadoPedidoUnitofWork
from app.modules.Producto.unit_of_work import ProductoUnitofWork
from app.modules.HistorialPedido.unit_of_work import HistorialEstadoPedidoUnitofWork
from app.modules.HistorialPedido.schemas import HistorialEstadoPedidoPublic, HistorialEstadoPedidoList

import logging
# Logger del módulo para trazabilidad de transiciones y eventos
logger = logging.getLogger("app.modules.Pedido.service")


class PedidoService:

    ##Inicia servecie
    def __init__(self, session: Session) -> None:
        
        self._session = session

##obtenemos un pedido por su id sino retruna error 404
    def _get_or_404(self, uow: PedidoUnitofWork, pedido_id: int) -> Pedido:
        
       
        pedido = uow.pedidos.get_by_id(pedido_id)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"pedido con id={pedido_id} no encontrado",
            )
        return pedido
   
    ###Obtenemos los activos
    def get_all(self, offset: int = 0, limit: int = 10) -> PedidoList:
        with PedidoUnitofWork(self._session) as uow:
            pedidos = uow.pedidos.get_active(
              offset=offset,
               limit=limit
        )

        total = uow.pedidos.count()

        result = PedidoList(
            data=[
                PedidoPublic.model_validate(i)
                for i in pedidos            
            ],
            total=total,
        )

        return result
    
    def list_all(self) -> list[PedidoPublic]:
        with PedidoUnitofWork(self._session) as uow:
            pedidos = uow.pedidos.get_active()
            return [PedidoPublic.model_validate(p) for p in pedidos]


        ##obtener ingrediente del produto segun su id
    def get_ingrediente_or_404(self,uow:PedidoUnitofWork, ingrediente_id:int):
        
        ingrediente = uow.ingredientes.get_by_id(ingrediente_id)
        if not ingrediente:
            raise HTTPException(
                status_code=404,
                detail=f"Ingredienet con id={ingrediente_id} no encontrado"
            )
        return ingrediente
    
    def get_categoria_or_404(self,uow:PedidoUnitofWork, categoria_id:int):
        
        categoria = uow.categorias.get_by_id(categoria_id)
        if not categoria:
            raise HTTPException(
                status_code=404,
                detail=f"categoria con id={categoria_id} no encontrado"
            )
        return categoria
    

    def get_ingrediente_perosnalizables(self,uow:PedidoUnitofWork,ingrediente_id:int):  ##Obtener un ingrediente personalizable
        ingrediente = uow.ingredientes.get_by_personable(ingrediente_id)
        if not ingrediente:
            raise HTTPException(
                status_code=404,
                detail=f"ingrediente con id ={ingrediente_id} no encontrado"
            )
        return ingrediente
##Obten buscar por id

    def get_by_id(self, pedido_id: int) -> PedidoPublic:
        
        with PedidoUnitofWork(self._session) as uow:
            pedido = self._get_or_404(uow, pedido_id)
            result = PedidoPublic.model_validate(pedido)

        return result    
    def obtener_precio(self, producto_id):  ##fucion para obtener el precio de la bases de dtaos de producto

      with DetallePedidoUnitofWork(self._session) as uow:

        return uow.detalle_pedidos.obtener_precio_producto(producto_id )

    def _obtener_nombre(self, producto_id):  ##fucion para obtener el nombre de la bases de dtaos de producto

      with DetallePedidoUnitofWork(self._session) as uow:

        return uow.detalle_pedidos.obtener_nombre_producto(producto_id )         
    
   # def obtener_cantidad_detalles_pedido(self, pedido_id):  ##fucion para obtener el nombre de la bases de dtaos de producto

    #  with DetallePedidoUnitofWork(self._session) as uow:

       # return uow.detalle_pedidos.get_cantidad_detalles_pedido(pedido_id ) 
    def _obtener_valor_cantidad_detalles_pedido(self, detalle_id: int):  ##fucion para obtener el nombre de la bases de dtaos de producto
        with DetallePedidoUnitofWork(self._session) as uow:
            return uow.detalle_pedidos.obtener_cantidad(detalle_id)

    def _restar_stock(self,uow:DetallePedidoUnitofWork,producto_id,cantidad) ->int:
        stock= uow.detalle_pedidos.obtener_stock_producto(producto_id)
        if stock is None:
            raise HTTPException(
                status_code=404,
                detail=f"producto s con id ={producto_id} no encontrado"
            )
        
        if stock>= cantidad:
            stock -=cantidad
            return stock
        raise HTTPException(
                   status_code=409,
                   detail=f"stock negativo es decir no hay disponibilidad"
        )
    
    def _restar_stock_ingrediente(self,uow:DetallePedidoUnitofWork,ingrediente_id,cantidad,producto_id) ->float:
        stock= uow.detalle_pedidos.obtener_stock_ingrediente(ingrediente_id)
        cantidad_ingrediente = uow.detalle_pedidos.cantidad_ingrediente_producto(ingrediente_id, producto_id)
        if stock is None:
            raise HTTPException(
                status_code=404,
                detail=f"producto s con id ={ingrediente_id} no encontrado"
            )
        
        if stock>= cantidad*cantidad_ingrediente:
            stock -=cantidad*cantidad_ingrediente
            return stock
        raise HTTPException(
                   status_code=409,
                   detail=f"stock negativo es decir no hay disponibilidad"
        )
    def _es_ingrediente_removible(self,uow:DetallePedidoUnitofWork,ingrediente_id) -> bool:
        es_removible= uow.detalle_pedidos.is_ingrediente_removible(ingrediente_id)
        if es_removible is None:
            raise HTTPException(
                status_code=404,
                detail=f"ingrediente con id ={ingrediente_id} no encontrado"
            )
        return es_removible
            
    def listar_pedidos_por_estado(self,estado_codigo,offset: int = 0, limit: int = 10)-> PedidoList:
        with PedidoUnitofWork (self._session) as uow:
            lista_estados_pedidos = uow.pedidos.get_pedidos_by_estado(estado_codigo,offset=offset,
               limit=limit)
            
        total = uow.pedidos.count()

        result = PedidoList(
            data=[
                PedidoPublic.model_validate(i)
                for i in lista_estados_pedidos           
            ],
            total=total,
        )

        return result
    
    def list_cocina_pedidos(self) -> list[PedidoPublic]:
        with PedidoUnitofWork(self._session) as uow:
            pedidos = [
                p for p in uow.pedidos.get_active()
                if p.estado_codigo in ("CONFIRMADO", "EN_PREP")
            ]
            pedidos.sort(key=lambda p: p.id or 0)
            return [PedidoPublic.model_validate(p) for p in pedidos]


           

 
##crea pedido

    def create(self, data: PedidoCreate) -> PedidoPublic:
        
       
        with PedidoUnitofWork(self._session) as uow:
           
                pedido = Pedido (**data.model_dump(exclude={"detalles"}))  ##valido pedido a basee de datoos

                pedido.detalles = []  ##paso la lista vacia

                total_pedido = Decimal("0.00")
            
                for detalle_pedido in data.detalles: ##recoerre los ingredientes agregados en el detalle create
                 
                    detalle_baseDatos= DetallePedido( producto_id=detalle_pedido.producto_id,
                     cantidad=detalle_pedido.cantidad) #Transforma el detalle pedid en datoas para la base

                    precio= self.obtener_precio(detalle_pedido.producto_id) ##obtengo el precio mediante la fcucion
                    nombre= self._obtener_nombre(detalle_pedido.producto_id) ##obtengo el nombre mediante la fcucion
                    detalle_baseDatos.nombre_snapshot=nombre ##cargo a la base de datos el valor de nombre
                    detalle_baseDatos.precio_snapshot=precio ##cargo a la base de datos el valor de precio
                    detalle_baseDatos.subtotal_snap=(precio*detalle_baseDatos.cantidad) 
                    total_pedido = total_pedido + detalle_baseDatos.subtotal_snap ## MODIFICADO || calculo el total del pedido sumando el subtotal de cada detalle pedido
                    ##Calcuñlo el subtotal y se guarda en bases de datos
                    #if data.estado_codigo=="ENTREGADO" : ##si el estado del pedido es entregado se descuenta el stock
                     #   nuevo_stock = self._restar_stock(uow,detalle_pedido.producto_id,detalle_pedido.cantidad)##restar stock
                      #  producto = uow.productos.get_by_id(detalle_pedido.producto_id) ##obtener producto
                       # producto.stock_cantidad = nuevo_stock
                        #uow.detalle_pedidos.add(detalle_baseDatos) ##guardo el cambio en la base de datos SACAR
                    detalle_baseDatos.personalizacion=[] # dentor de cada detalle pedido puedo elegir ingredientes a perosnalizar AGREGAR ARRIBA DE SNAPpRECIO
                    for personalizado in detalle_pedido.personalizacion: ##recooro la lista del detalle create que cargo el usuario 
                        removible= self.get_ingrediente_perosnalizables(uow,personalizado) ##uso la fucion para obtener el ingrediente reciebe como para parametro el entero que cargo el usuariioo
                        detalle_baseDatos.personalizacion.append(removible.id) ## guardo en le lista de al basees de datos de los persoanlizables



                  
                   
                 
                    pedido.detalles.append(detalle_baseDatos)##guardamos el ingredeinte en ela lista que ira  a la base de datos
                       
           

            
           
                pedido.total = total_pedido ##cargo el total del pedido en la base de datos
                uow.pedidos.add(pedido)

            

                # obtener id generado
        self._session.flush()

        # ---------- HISTORIAL INICIAL ----------
        historial = HistorialEstadoPedido(
            pedido_id=pedido.id,
            estado_desde=None,
            estado_hacia=pedido.estado_codigo,
            usuario_id=pedido.usuario_id,
            motivo="Pedido creado"
        )
        uow.historial_estado_pedido.add(historial)


       # self._session.add(historial)
        # ---------------------------------------

       # uow.commit()






        result = PedidoPublic.model_validate(pedido)

        return result
    

    ###Modificador####falta cooregir
    
    def update(self, pedido_id:int, data:PedidoUpdate)->PedidoPublic:

     with PedidoUnitofWork(self._session) as uow:

        pedido = self._get_or_404(uow,pedido_id) ##obtenemos el pedido a modificar sino existe error 404

        patch = { # diccionario con los campos a modificar
            k:v
            for k,v in data.model_dump(exclude_unset=True).items()  #solo incluye los campos que el usuario envio en la peticion, si el usuario no envio un campo ese campo no se incluye en el diccionario
            if v not in (None,"")
        }

        nuevo_estado = patch.get("estado_codigo") ##obtenemos el nuevo estado del diccionario de campos a modificar, si el usuario no envio el campo estado_codigo entonces nuevo_estado sera None

        estado_nuevo = uow.estado_pedido.get_by_codigo(nuevo_estado) ##obtenemos el nuevo estado de la base de datos, si nuevo_estado es None entonces estado_nuevo sera None
        
        if estado_nuevo is None:
            raise HTTPException(
        404,
        "Estado no encontrado")

        estado_actual = uow.estado_pedido.get_by_codigo( #obtenemos el estado actual del pedido de la base de datos, si el pedido no tiene estado entonces estado_actual sera None
            pedido.estado_codigo)

        if estado_actual.es_terminal: ##un estado terminal (ENTREGADO/CANCELADO) no admite mas transiciones
            raise HTTPException(
                400,
                "Cambio de estado no permitido"
            )

        es_secuencial = estado_nuevo.orden - estado_actual.orden == 1 ##avance normal al siguiente estado
        es_cancelacion = nuevo_estado == "CANCELADO" ##se puede cancelar desde cualquier estado no terminal

        if not (es_secuencial or es_cancelacion):
            raise HTTPException(
                400,
                "Cambio de estado no permitido"
            )

        if nuevo_estado == "ENTREGADO" and pedido.estado_codigo != "ENTREGADO": ##si el nuevo estado es entregado y el estado actual no es entregado entonces se descuenta el stock de los productos del pedido

            for detalle in pedido.detalles:

                producto = uow.productos.get_by_id(detalle.producto_id)

                if producto is None:
                    raise HTTPException(status_code=404, detail=f"Producto {detalle.producto_id} no encontrado")

                producto.stock_cantidad = self._restar_stock(
                    uow,
                    detalle.producto_id,
                    detalle.cantidad
                )

                uow.productos.add(producto)
                for ingrediente in detalle.producto.ingredientes:
                   ## ingrediente = uow.ingredientes.get_by_id(ingrediente_id)

                    if ingrediente is None:
                        raise HTTPException(status_code=404, detail=f"Ingrediente {ingrediente.id} no encontrado")
                    
                   
                    if ingrediente  not in detalle.personalizacion: ##si el ingrediente no esta en la lista de personalizacion del detalle pedido entonces se descuenta su stock
                         ingrediente.stock_cantidad = self._restar_stock_ingrediente(
                          uow,
                          ingrediente.id,
                          detalle.cantidad,
                          detalle.producto_id
                    )

                    uow.ingredientes.add(ingrediente)
       

        historial = HistorialEstadoPedido(
            pedido_id=pedido.id,
            estado_desde=pedido.estado_codigo,
            estado_hacia=nuevo_estado,
            usuario_id=data.usuario_id,
            motivo=data.notas or f"Cambio a {nuevo_estado}"
        )

        uow.historial_estado_pedido.add(historial)

        for field,value in patch.items():
            setattr(pedido,field,value)

        uow.pedidos.add(pedido)

     return PedidoPublic.model_validate(pedido)
    
    async def avanzar_estado(self, pedido_id: int, nuevo_estado: str, current_user) -> PedidoPublic:
        data = PedidoUpdate(estado_codigo=nuevo_estado, usuario_id=current_user.id)
        return self.update(pedido_id, data)


    ##eliminar
    def soft_delete(self, pedido_id: int) -> None:
        
        with PedidoUnitofWork(self._session) as uow:
            pedido= self._get_or_404(uow, pedido_id)
            pedido.is_active = False
            uow.pedidos.add(pedido)

     #HISTORIAL ESTADOS
    def get_all_historial_estado_pedido(self, offset: int, limit: int) -> HistorialEstadoPedidoList:
        with HistorialEstadoPedidoUnitofWork(self._session) as uow:
            historial = uow.historial_estado_pedido.get_all(offset, limit )

        total = uow.historial_estado_pedido.count_sin_filtro() 
        
     

        result = HistorialEstadoPedidoList(
            data=[
                HistorialEstadoPedidoPublic.model_validate(i)
                for i in historial              
            ],
            total=total,
        )

        return result
    


    #FORMADEPAGO

    def get_all_forma_pago(self, offset: int, limit: int):
        with PedidoUnitofWork(self._session) as uow:
            formas_pago = uow.forma_pago.get_habilitados(offset, limit)
        total = uow.forma_pago.count_habilitados()
        result = {
            "data": [forma_pago for forma_pago in formas_pago],     
            "total": total
        }

        return result