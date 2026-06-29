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
from app.modules.usuarios.schemas import UserPublic

import logging
# Logger del módulo para trazabilidad de transiciones y eventos
logger = logging.getLogger("app.modules.Pedido.serviceWebsocket")

# =============================================================================
# NORMALIZACIÓN DE ESTADOS
# =============================================================================
#
# Unifica variaciones de entrada (inglés, mayúsculas, abreviaturas) a valores
# canónicos en minúsculas. Esto permite que el frontend envíe "Pendiente",
# "pending" o "PENDIENTE" y siempre se resuelva a "pendiente".
#
# Ejemplo de uso:
#   estado_db = "PENDIENTE"
#   estado_normalizado = ESTADOS.get(estado_db, estado_db)  # → "pendiente"
#
ESTADOS = {
    # Español
    "pendiente": "pendiente",
    "confirmado": "confirmado",
    "preparando": "preparando",
    "enviado": "enviado",
    "entregado": "entregado",
    "cancelado": "cancelado",
    # Inglés
    "pending": "pendiente",
    "confirmed": "confirmado",
    "shipped": "enviado",
    "delivered": "entregado",
    "cancelled": "cancelado",
    # Abreviaturas
    "en_prep": "preparando",
    "en_preparacion": "preparando",
    "en_camino": "listo",
    "listo": "listo",
    "ready": "listo",
    # Backward-compat (pedidos viejos en BD con estado enviado)
    "enviado": "listo",
}


# =============================================================================
# FSM + PERMISOS POR ROL (TRANSICIONES)
# =============================================================================
#
# Diccionario unificado que define:
#   - Qué transiciones puede hacer cada rol (RBAC)
#   - Qué transiciones son válidas según el estado actual (FSM)
#
# Estructura: TRANSICIONES[ROL][ESTADO_ACTUAL] = {estados_destino_posibles}
#
# Si un rol no está en el dict → no tiene permisos para avanzar estados.
# Si un estado no está en las keys del rol → no admite transiciones desde ahí.
#
# Ejemplo de lookup:
#   rol = "COCINA"
#   origen = "confirmado"
#   permitidos = TRANSICIONES.get("COCINA", {}).get("confirmado", set())
#   # → {"preparando"}
#   if "preparando" not in permitidos:
#       raise HTTPException(403, "Transición no permitida")
#
TRANSICIONES = {
    # Admin puede hacer CUALQUIER transición válida
    "ADMIN": {
        "pendiente":  {"confirmado", "cancelado"},
        "confirmado": {"preparando", "cancelado"},
        "preparando": {"listo", "cancelado"},
        "listo":      {"entregado", "cancelado"},
        "entregado":  set(),   # Estado terminal — no admite transiciones
        "cancelado":  set(),   # Estado terminal — no admite transiciones
    },
    # Pedidos: confirma, manda a cocina y entrega cuando está listo
    "PEDIDOS": {
        "pendiente":  {"confirmado", "cancelado"},
        "confirmado": {"preparando", "cancelado"},
        "preparando": set(),            # La cocina se encarga — cajero no avanza de aquí
        "listo":      {"entregado"},    # Cajero entrega cuando cocina lo marca listo
        "entregado":  set(),
        "cancelado":  set(),
    },
    # Cocina marca el pedido como listo para que el cajero lo entregue
    "COCINA": {
        "preparando": {"listo"},        # Marcar como listo para entrega
    },
}


# =============================================================================
# EVENTOS WebSocket
# =============================================================================
#
# Mapea cada estado destino al nombre del evento WebSocket que se envía
# al frontend. Los nombres siguen convención SCREAMING_SNAKE_CASE.
#
# Estos eventos son los que el frontend KDS escucha en socket.onmessage.
#
EVENTOS_WS = {
    "pendiente":  "NUEVO_PEDIDO",
    "confirmado": "PEDIDO_CONFIRMADO",
    "preparando": "PEDIDO_EN_PREPARACION",
    "listo":      "PEDIDO_LISTO",
    "cancelado":  "PEDIDO_CANCELADO",
    "entregado":  "PEDIDO_ENTREGADO",
}


# =============================================================================
# ROLES POR TRANSICIÓN (para emisión WebSocket)
# =============================================================================
#
# Define qué roles de staff deben ser notificados cuando un pedido llega
# a cada estado. La room del pedido (order:{orderId}) SIEMPRE se notifica,
# esto es solo para las rooms de rol.
#
# Lógica de negocio detrás de cada regla:
#   - confirmado → pedidos + cocina
#     El cajero confirmó el pago, la cocina debe saber que hay un nuevo pedido
#
#   - preparando → cocina + pedidos
#     La cocina inició la preparación, pedidos monitorea el progreso
#
#   - enviado → pedidos
#     El pedido salió a delivery, solo pedidos necesita saber
#
#   - entregado → pedidos
#     El pedido llegó al cliente, solo pedidos necesita saber
#
#   - cancelado → pedidos + cocina
#     Todos los involucrados deben saber que se canceló
#
ROLES_POR_TRANSICION = {
    "pendiente":  ["pedidos", "admin"],
    "confirmado": ["pedidos", "cocina", "admin"],
    "preparando": ["cocina", "pedidos", "admin"],
    "listo":      ["pedidos", "admin"],   # Cajero recibe aviso para entregar
    "entregado":  ["pedidos", "admin"],
    "cancelado":  ["pedidos", "cocina", "admin"],
}


# =============================================================================
# CLASE DE SERVICIO
# =============================================================================
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
    
    ##crea pedido

    async def create(self, data: PedidoCreate) -> PedidoPublic:
        
       
        with PedidoUnitofWork(self._session) as uow:
           
                pedido = Pedido (**data.model_dump(exclude={"detalles"}))  ##valido pedido a basee de datoos

                pedido.detalles = []  ##paso la lista vacia
            
                for detalle_pedido in data.detalles: ##recoerre los ingredientes agregados en el detalle create
                 
                    detalle_baseDatos= DetallePedido( producto_id=detalle_pedido.producto_id,
                     cantidad=detalle_pedido.cantidad) #Transforma el detalle pedid en datoas para la base

                    precio= self.obtener_precio(detalle_pedido.producto_id) ##obtengo el precio mediante la fcucion
                    nombre= self._obtener_nombre(detalle_pedido.producto_id) ##obtengo el nombre mediante la fcucion
                    detalle_baseDatos.nombre_snapshot=nombre ##cargo a la base de datos el valor de nombre
                    detalle_baseDatos.precio_snapshot=precio ##cargo a la base de datos el valor de precio
                    detalle_baseDatos.subtotal_snap=(precio*detalle_baseDatos.cantidad) 
                    total_pedido = Decimal(str(pedido.total)) + detalle_baseDatos.subtotal_snap ##calculo el total del pedido sumando el subtotal de cada detalle pedido
                    ##Calcuñlo el subtotal y se guarda en bases de datos
                    if data.estado_codigo=="ENTREGADO" : ##si el estado del pedido es entregado se descuenta el stock
                        nuevo_stock = self._restar_stock(uow,detalle_pedido.producto_id,detalle_pedido.cantidad)##restar stock
                        producto = uow.productos.get_by_id(detalle_pedido.producto_id) ##obtener producto
                        producto.stock_cantidad = nuevo_stock
                        uow.detalle_pedidos.add(detalle_baseDatos) ##guardo el cambio en la base de datos SACAR
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
        await self._emit_ws_events(result.id, "pendiente", result)
        return result
    
    def list_cocina_pedidos(self) -> list[PedidoPublic]:
        """
        Obtiene la lista de pedidos activos para la pantalla de cocina (KDS).

        Reglas de negocio:
          - Solo estados activos de cocina: "confirmado" o "preparando"
          - Ordenados por antigüedad (ID ascendente) — primero los más viejos

        Este endpoint se usa tanto para el carga inicial del KDS (REST)
        como para el polling de respaldo cuando se cae el WebSocket.
        """
        with PedidoUnitofWork(self._session) as uow:
            all_pedidos = uow.pedidos.get_all()
            cocina_pedidos = [
                p for p in all_pedidos
                if p.estado in ("preparando", "EN_PREP", "en_preparacion")
            ]
            cocina_pedidos.sort(key=lambda p: p.id or 0)
            result = [PedidoPublic.model_validate(p) for p in cocina_pedidos]
        return result
    async def avanzar_estado(
        self, pedido_id: int, nuevo_estado: str, current_user: UserPublic,data:PedidoUpdate
    ) -> PedidoPublic:
        """
        Avanza el estado de un pedido aplicando FSM + RBAC en un solo lookup.

        Este es el método MÁS IMPORTANTE del servicio — orquesta:
          1. Validación de existencia del pedido
          2. Normalización de estados (inglés/español/abreviaturas)
          3. Validación FSM + RBAC en un solo lookup O(1)
          4. Persistencia del cambio en BD (dentro de UoW)
          5. Auditoría en logs
          6. Emisión de eventos WebSocket a rooms relevantes

        Args:
            pedido_id:    ID del pedido a actualizar
            nuevo_estado: Estado destino (se normaliza vía dict ESTADOS)
            current_user: Usuario autenticado que realiza la transición

        Raises:
            HTTPException 404: si el pedido no existe
            HTTPException 403: si la transición no está permitida para el rol

        Returns:
            PedidoPublic con el estado actualizado
        """

        with PedidoUnitofWork(self._session) as uow:
            # ─── PASO 1: Buscar el pedido ─────────────────────────────────────
            pedido = self._get_or_404(uow,pedido_id) ##obtenemos el pedido a modificar sino existe error 404

            # ─── PASO 2: Normalizar estados ───────────────────────────────────
            # Convierte variaciones a valores canónicos en minúsculas
            # Ejemplo: "PENDIENTE" → "pendiente", "en_prep" → "preparando"
            
            origen = pedido.estado_codigo.lower()
            destino = nuevo_estado.lower()

            origen = ESTADOS.get(origen, origen)
            destino = ESTADOS.get(destino, destino)
            pedido.estado_codigo = destino


            # Si el origen y destino son iguales, no hay nada que hacer
            if origen == destino:
                return PedidoPublic.model_validate(pedido)

            # ─── PASO 3: Validar FSM + RBAC en un solo lookup ────────────────
            # Este es el corazón de la validación:
            #   TRANSICIONES[ROL][ESTADO_ORIGEN] → {estados_destino_permitidos}
            #
            # Si el rol no está en el dict → set() vacío → 403
            # Si el estado no está en las keys del rol → set() vacío → 403
            # Si el destino no está en el set → 403
            #
            # Complejidad: O(1) — un solo lookup en dict anidado
            #
            rol = current_user.role.upper().strip()
            permitidos = TRANSICIONES.get(rol, {}).get(origen, set())

            if destino not in permitidos:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Transición no permitida para tu rol: '{pedido.estado}' → '{nuevo_estado}'",
                )

            # ─── PASO 4: Auditoría ────────────────────────────────────────────
            # Log detallado para trazabilidad y cumplimiento
            logger.info(
                f"AUDITORÍA FSM: Usuario {current_user.username} "
                f"(ID: {current_user.id}, Rol: {current_user.role}) "
                f"avanzó pedido {pedido_id} de '{pedido.estado}' a '{nuevo_estado}'"
            )


            #descontar stocks
            
            if destino == "entregado" and origen != "entregado": ##si el nuevo estado es entregado y el estado actual no es entregado entonces se descuenta el stock de los productos del pedido

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
       
            # historial 

            historial = HistorialEstadoPedido(
            pedido_id=pedido.id,
            estado_desde=pedido.estado_codigo,
            estado_hacia=nuevo_estado,
            usuario_id=data.usuario_id,
            motivo=data.notas or f"Cambio a {nuevo_estado}"
        )

            uow.historial_estado_pedido.add(historial)
            


            # ─── PASO 5: Persistir el cambio ──────────────────────────────────
            pedido.estado_codigo = destino
            uow.pedidos.update(pedido)
            result = PedidoPublic.model_validate(pedido)

        # ─── PASO 6: Emitir eventos WebSocket (FUERA del bloque transaccional) ─
        # Se emite después del commit del UoW para asegurar que los datos
        # estén persistidos antes de notificar a los clientes.
        await self._emit_ws_events(pedido_id, destino, result)

        return result
    async def _emit_ws_events(
        self, pedido_id: int, destino: str, result: PedidoPublic
    ) -> None:
        """
        Emite eventos WebSocket a las rooms relevantes según el estado destino.

        Este método implementa la lógica de notificación selectiva:
          1. SIEMPRE emite a la room del pedido (order:{orderId})
             → El cliente que hizo el pedido recibe la actualización
          2. Emite a las rooms de los roles relevantes
             → El personal recibe solo lo que le compete

        El evento incluye el pedido completo serializado como diccionario,
        para que el frontend pueda actualizar su estado local sin hacer
        un fetch adicional a la API REST.

        Args:
            pedido_id: ID del pedido (para la room order:{id})
            destino:   Estado al que se transitionó (para mapear el evento)
            result:    PedidoPublic con los datos actualizados
        """
        from app.core.websocket import manager

        # Mapear estado destino → nombre del evento WebSocket
        # Si el estado no tiene evento asociado (ej: "pendiente"), no se emite
        event_type = EVENTOS_WS.get(destino)
        if not event_type:
            return

        # Serializar el pedido a diccionario para enviar como JSON
        data = result.model_dump()

        # ─── NOTIFICAR AL CLIENTE (room del pedido) ──────────────────────────
        # El cliente que hizo el pedido siempre recibe la actualización,
        # sin importar qué rol procesó el cambio.
        #
        # Ejemplo: si el pedido #5 pasó a "confirmado":
        #   broadcast_to_order(5, "PEDIDO_CONFIRMADO", pedido_data)
        #   → El socket del cliente en "order:5" recibe el evento
        #
        await manager.broadcast_to_order(pedido_id, event_type, data)

        # ─── NOTIFICAR A LOS ROLES RELEVANTES ───────────────────────────────
        # Cada transición notifica a los roles que necesitan saber el cambio.
        # La configuración está en ROLES_POR_TRANSICION.
        #
        # Ejemplo: si el pedido pasó a "confirmado":
        #   broadcast_to_roles(["pedidos", "cocina"], "PEDIDO_CONFIRMADO", data)
        #   → Los sockets en "role:pedidos" y "role:cocina" reciben el evento
        #   → Un socket que esté en ambas rooms solo recibe una vez (deduplicación)
        #
        roles_a_notificar = ROLES_POR_TRANSICION.get(destino, [])
        if roles_a_notificar:
            await manager.broadcast_to_roles(roles_a_notificar, event_type, data)

        logger.info(
            f"WS emitido: {event_type} | pedido={pedido_id} | "
            f"roles={roles_a_notificar} | rooms_activas={manager.get_rooms_info()}"
        )
    



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
