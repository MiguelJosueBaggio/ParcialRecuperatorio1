from fastapi import HTTPException, status
from sqlmodel import Session

from app.modules.Pedido.models import Pedido
from app.modules.DetallePedido.models import DetallePedido

from app.modules.Pedido.schemas import PedidoCreate, PedidoPublic, PedidoUpdate, PedidoList, DetallePedidoCreate, DetallePedidoPublic
from app.modules.Pedido.unit_of_work import PedidoUnitofWork
from app.modules.DetallePedido.unit_of_work import DetallePedidoUnitofWork
from app.modules.EstadoPedido.unit_of_work import EstadoPedidoUnitofWork
from app.modules.Producto.unit_of_work import ProductoUnitofWork
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
        
            
    def listar_estados(self,estado_codigo,offset: int = 0, limit: int = 10)-> PedidoList:
        with PedidoUnitofWork (self._session) as uow:
            lista_estados_pedidos = uow.get_estado_pedido(estado_codigo,offset=offset,
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

           

 
##crea pedido

    def create(self, data: PedidoCreate) -> PedidoPublic:
        
       
        with PedidoUnitofWork(self._session) as uow:
           
                pedido = Pedido.model_validate(data)  ##valido pedido a basee de datoos

                pedido.detalles_pedido = []  ##paso la lista vacia
            
                for detalle_pedido in data.detalles_pedido: ##recoerre los ingredientes agregados en el detalle create
                 
                    detalle_baseDatos= DetallePedido.model_validate(detalle_pedido) #Transforma el detalle pedid en datoas para la base

                    precio= self.obtener_precio(detalle_pedido.producto_id) ##obtengo el precio mediante la fcucion

                    detalle_baseDatos.precio_snapshot=precio ##cargo a la base de datos el valor de precio
                    detalle_baseDatos.subtotal_snap=(precio*detalle_baseDatos.cantidad) ##Calcuñlo el subtotal y se guarda en bases de datos
                   ## if pedido.estado_pedido == "ENTREGADO":
                                                        ##    producto=uow.productos.get_by_id(detalle_baseDatos.producto_id)

                                                          ##  producto.stock_cantidad = self._restar_stock(uow,detalle_baseDatos.producto_id,detalle_baseDatos.cantidad)##restar stock
                   
                    detalle_baseDatos.personalizacion=[] # dentor de cada detalle pedido puedo elegir ingredientes a perosnalizar AGREGAR ARRIBA DE SNAPpRECIO
                    for personalizado in detalle_pedido.personalizacion: ##recooro la lista del detalle create que cargo el usuario 
                        removible= self.get_ingrediente_perosnalizables(uow,personalizado) ##uso la fucion para obtener el ingrediente reciebe como para parametro el entero que cargo el usuariioo
                        detalle_baseDatos.personalizacion.append(removible) ## guardo en le lista de al basees de datos de los persoanlizables



                  
                   
                 
                    pedido.detalles_pedido.append(detalle_baseDatos)##guardamos el ingredeinte en ela lista que ira  a la base de datos

           

            
           
            
                uow.pedidos.add(pedido)

            
                result = PedidoPublic.model_validate(pedido)

        return result
    

    ###Modificador####falta cooregir
    
    def update(self, pedido_id: int, data: PedidoUpdate) -> PedidoPublic:
      with PedidoUnitofWork(self._session) as uow:
        pedido = self._get_or_404(uow, pedido_id) ##BUSCO EL PEDIDO
        
       
       

        # 🔹 Campos simples (excluyendo relaciones)
        patch = data.model_dump() ##TRANFORMO A DICCIONARO

        if patch.get("estado_codigo")=="ENTREGADO" and pedido.estado_codigo != "ENTREGADO": #EVALUO SI EL ESTADO ES ENTREGADO EN EL UPDATE Y ADMAS QUE EN LA BASE DE DATOS SEA DIFERENTE A ENTREGADA PARA EVITAR DESCUENTOS POR DUPLICADO
            for detalle in pedido.detalles_pedido: ##BUSSCO EN TODOS LOS DETALLES
                detalle.producto.stock_cantidad = self._restar_stock (uow,detalle.producto_id,detalle.cantidad) #APLICO LA FORMULA DE DESCONTAR PEDIDO
            

        for field, value in patch.items():
            setattr(pedido, field, value)
        
      

        uow.pedidos.add(pedido)
      
            

      return PedidoPublic.model_validate(pedido)


    ##eliminar
    def soft_delete(self, pedido_id: int) -> None:
        
        with PedidoUnitofWork(self._session) as uow:
            pedido= self.get_or_404(uow, pedido_id)
            pedido.is_active = False
            uow.pedidos.add(pedido)