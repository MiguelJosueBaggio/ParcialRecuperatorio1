import logging
import uuid
from decimal import Decimal

import mercadopago
from fastapi import HTTPException, status
from sqlmodel import Session

from app.core.config import settings

from app.modules.Pago.models import Pago, EstadoPago
from app.modules.Pago.schemas import CrearPreferenciaResponse, PagoPublic, PagoList
from app.modules.Pago.unit_of_work import PagoUnitofWork

from app.modules.HistorialPedido.models import HistorialEstadoPedido

logger = logging.getLogger("app.modules.Pago.service")


# Mapeo del `status` que devuelve la API de pagos de MercadoPago
# hacia el EstadoPago interno. Ver: https://www.mercadopago.com.ar/developers
# -> valores posibles: approved, pending, in_process, rejected, cancelled,
# refunded, charged_back, authorized.
_MP_STATUS_MAP: dict[str, EstadoPago] = {
    "approved": EstadoPago.APROBADO,
    "pending": EstadoPago.PENDIENTE,
    "in_process": EstadoPago.EN_PROCESO,
    "authorized": EstadoPago.EN_PROCESO,
    "rejected": EstadoPago.RECHAZADO,
    "cancelled": EstadoPago.CANCELADO,
    "refunded": EstadoPago.CANCELADO,
    "charged_back": EstadoPago.CANCELADO,
}

# Único avance de FSM que dispara la confirmación de un pago:
# PENDIENTE(1) -> CONFIRMADO(2). Respeta la regla orden_nuevo - orden_actual == 1
# que ya usa PedidoService.update().
# NOTA: pendiente de confirmar con la cátedra si el estado destino real
# debería ser otro (ver charla sobre Pedido.estado_codigo vs "pagado").
_ESTADO_PEDIDO_AL_APROBAR = "CONFIRMADO"
_ESTADO_PEDIDO_AL_RECHAZAR = "CANCELADO"

# Topics de webhook que nos interesan procesar. MercadoPago manda
# notificaciones de muchos otros tipos de eventos (suscripciones, etc.)
# que no son relevantes para Checkout Pro simple.
_WEBHOOK_TOPICS_VALIDOS = (None, "payment", "merchant_order")


class PagoService:

    def __init__(self, session: Session) -> None:
        self._session = session

    # ---------- helpers de configuración / SDK de MercadoPago ----------
    #
    # Mismo principio que la slide "El módulo de pagos": la lógica de
    # negocio (el resto de esta clase) nunca llama al SDK directamente,
    # siempre pasa por estos métodos privados. Se crea el SDK on-demand
    # en cada llamada (no a nivel de módulo/import) para que sea más
    # fácil testear con mocks y no depender de que las env vars ya estén
    # cargadas en el momento del import.

    def _get_mp_access_token(self) -> str:
        if not settings.MP_ACCESS_TOKEN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MercadoPago no configurado. Configure MP_ACCESS_TOKEN",
            )
        return settings.MP_ACCESS_TOKEN

    def _get_mp_public_key(self) -> str:
        return settings.MP_PUBLIC_KEY

    def _get_mp_sdk(self) -> "mercadopago.SDK":
        return mercadopago.SDK(self._get_mp_access_token())

    def _crear_preferencia_mp(
        self,
        *,
        monto: Decimal,
        titulo: str,
        pedido_id: int,
        external_reference: str,
        idempotency_key: str,
        back_urls: dict[str, str],
    ) -> dict:
        """'Crear preferencia': registra el pedido de cobro en MercadoPago."""
        preference_data = {
            "items": [
                {
                    "title": titulo,
                    "quantity": 1,
                    "unit_price": float(monto),
                    "currency_id": "ARS",
                }
            ],
            "external_reference": external_reference,
            "back_urls": back_urls,
            "auto_return": "approved",
            "notification_url": f"{settings.NGROK_URL}/pagos/webhook",
        }

        request_options = mercadopago.config.RequestOptions()
        request_options.custom_headers = {"x-idempotency-key": idempotency_key}

        try:
            result = self._get_mp_sdk().preference().create(preference_data, request_options)
        except Exception as exc:
            raise RuntimeError(f"Error de conexión con MercadoPago: {exc}")

        if result["status"] not in (200, 201):
            raise RuntimeError(f"Error creando preferencia en MercadoPago: {result}")

        return result["response"]

    def _consultar_pago_mp(self, mp_payment_id: int) -> dict:
        """
        'Verificar estado': consulta el estado real de un pago contra la
        API de MercadoPago. Nunca se confía en parámetros de URL ni en el
        body del webhook sin esta verificación.
        """
        try:
            result = self._get_mp_sdk().payment().get(mp_payment_id)
        except Exception as exc:
            raise RuntimeError(f"Error de conexión con MercadoPago: {exc}")

        if result["status"] != 200:
            raise RuntimeError(f"Error consultando pago en MercadoPago: {result}")

        return result["response"]

    # ---------- helpers propios ----------

    def _get_or_404(self, uow: PagoUnitofWork, pago_id: int) -> Pago:
        pago = uow.pagos.get_by_id(pago_id)
        if not pago:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"pago con id={pago_id} no encontrado",
            )
        return pago

    def _generar_external_reference(self, pedido_id: int) -> str:
        # pedido-{id}-{8 hex} para legibilidad en el panel de MP y unicidad
        return f"pedido-{pedido_id}-{uuid.uuid4().hex[:8]}"

    def _generar_idempotency_key(self) -> str:
        return str(uuid.uuid4())

    def _mapear_estado_mp(self, mp_status: str | None) -> EstadoPago:
        return _MP_STATUS_MAP.get(mp_status, EstadoPago.EN_PROCESO)

    # ---------- "Crear pedido -> solicitar preferencia -> recibir init_point" ----------

    def crear_preferencia_para_pedido(self, pedido_id: int) -> CrearPreferenciaResponse:
        """
        Operación de negocio 'Crear pago'.

        1) Reserva un registro Pago en PENDIENTE con external_reference e
           idempotency_key propios. Esto se persiste ANTES de hablar con
           MercadoPago, así sobrevive aunque la llamada a MP falle después
           (permite reintentar sin duplicar ni perder el rastro).
        2) Recién con el Pago ya guardado, se llama a MercadoPago (única
           función aislada que lo hace) para crear la preferencia.
        3) Se actualiza el mismo registro con mp_preference_id y
           mp_init_point.
        """
        with PagoUnitofWork(self._session) as uow:
            pedido = uow.pedidos.get_by_id(pedido_id)
            if pedido is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"pedido con id={pedido_id} no encontrado",
                )

            if pedido.estado_codigo != "PENDIENTE":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        f"El pedido {pedido_id} está en estado "
                        f"'{pedido.estado_codigo}', no se puede generar "
                        f"un pago para él."
                    ),
                )

            pago = Pago(
                pedido_id=pedido_id,
                monto=pedido.total,
                estado=EstadoPago.PENDIENTE,
                external_reference=self._generar_external_reference(pedido_id),
                idempotency_key=self._generar_idempotency_key(),
            )
            uow.pagos.add(pago)
            # uow.commit() automático al salir del `with`. Hasta aquí: el
            # Pago en PENDIENTE queda persistido incluso si la llamada a
            # MP (paso siguiente) falla, permitiendo reintentar sin perder
            # el rastro del intento ni duplicar el external_reference.

        # Fuera del `with` anterior: la reserva local ya está confirmada.
        # Recién ahora se habla con MercadoPago (única función que lo hace).
        back_urls = {
            "success": f"{settings.NGROK_URL}/pagos/redirect/{pedido_id}/success",
            "failure": f"{settings.NGROK_URL}/pagos/redirect/{pedido_id}/failure",
            "pending": f"{settings.NGROK_URL}/pagos/redirect/{pedido_id}/pending",
        }

        try:
            mp_data = self._crear_preferencia_mp(
                monto=pago.monto,
                titulo=f"Pedido #{pedido_id} - FoodStore",
                pedido_id=pedido_id,
                external_reference=pago.external_reference,
                idempotency_key=pago.idempotency_key,
                back_urls=back_urls,
            )
        except RuntimeError as exc:
            logger.exception(f"Error creando preferencia MP para pedido {pedido_id}: {exc}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            )

        with PagoUnitofWork(self._session) as uow:
            pago_actualizado = uow.pagos.get_by_id(pago.id)
            pago_actualizado.mp_preference_id = mp_data["id"]
            pago_actualizado.mp_init_point = mp_data.get("init_point")
            uow.pagos.add(pago_actualizado)
            # segundo commit automático al salir del `with`.

        return CrearPreferenciaResponse(
            pago_id=pago.id,
            preference_id=mp_data["id"],
            init_point=mp_data.get("init_point"),
            external_reference=pago.external_reference,
        )

    # ---------- "Verificar estado -> Actualizar pedido" (confirmación por retorno) ----------

    def confirmar_pago(self, pedido_id: int, mp_payment_id: str | None = None) -> PagoPublic:
        """
        Llamado desde el endpoint /confirm cuando el usuario vuelve del
        checkout. El frontend conoce siempre pedido_id (viene en la URL
        de retorno); mp_payment_id es opcional porque MP no siempre lo
        manda como query param en el redirect.

        Si no se recibe mp_payment_id, se busca el último Pago registrado
        para ese pedido y se usa el mp_payment_id que ya tuviera guardado
        (por ejemplo, si el webhook ya llegó antes que el usuario volviera).
        """
        with PagoUnitofWork(self._session) as uow:
            pedido = uow.pedidos.get_by_id(pedido_id)
            if pedido is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Pedido no encontrado",
                )

            resolved_payment_id = mp_payment_id
            if not resolved_payment_id:
                pago_local = uow.pagos.get_ultimo_by_pedido(pedido_id)
                if pago_local and pago_local.mp_payment_id:
                    resolved_payment_id = str(pago_local.mp_payment_id)

        if not resolved_payment_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontró un payment_id para confirmar este pedido",
            )

        try:
            int(resolved_payment_id)
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"payment_id inválido: '{resolved_payment_id}' no es numérico",
            )

        try:
            mp_info = self._consultar_pago_mp(int(resolved_payment_id))
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            )

        return self._aplicar_resultado_pago(mp_info, pedido_id_hint=pedido_id)

    # ---------- Webhook IPN ----------

    def procesar_webhook(self, data: dict, query_params: dict | None = None) -> dict:
        """
        Notificación asíncrona de MercadoPago. Soporta los distintos
        formatos que MP puede mandar:
          - Webhooks nuevos:  {"type": "payment", "data": {"id": "123"}}
          - IPN legacy:       {"topic": "payment", "data_id": "123"}
          - Como query params: ?topic=payment&id=123

        Regla de oro: el router que llama a este método SIEMPRE responde
        200 OK a MP, sin importar lo que devuelva esta función.
        """
        query_params = query_params or {}
        logger.info(f"Webhook recibido: data={data}, qs={query_params}")

        if not data and query_params:
            data = query_params

        topic = data.get("type") or data.get("topic")
        data_id = data.get("data_id") or (data.get("data") or {}).get("id")
        payment_id = data.get("id")

        if not data_id and query_params:
            data_id = query_params.get("data.id") or query_params.get("id")
        if not topic and query_params:
            topic = query_params.get("topic") or query_params.get("type")

        pago_mp_id = payment_id or data_id

        if not pago_mp_id:
            return {"status": "ignored", "reason": "No payment ID"}

        if topic not in _WEBHOOK_TOPICS_VALIDOS:
            return {"status": "ignored", "reason": f"Topic: {topic}"}

        try:
            mp_info = self._consultar_pago_mp(int(pago_mp_id))
        except (RuntimeError, ValueError, TypeError) as exc:
            logger.exception(f"Error procesando webhook MP: {exc}")
            return {"status": "error", "reason": str(exc)}

        resultado = self._aplicar_resultado_pago(mp_info)
        return {
            "status": "processed",
            "pago_id": resultado.id,
            "estado": resultado.estado,
            "pedido_id": resultado.pedido_id,
        }

    # ---------- núcleo común: aplicar un resultado YA VERIFICADO contra MP ----------

    def _aplicar_resultado_pago(self, mp_info: dict, pedido_id_hint: int | None = None) -> PagoPublic:
        """
        Punto de convergencia único entre confirmar_pago() y
        procesar_webhook(): ambos terminan acá una vez que ya tienen la
        respuesta REAL de MercadoPago en mano (nunca se llama con datos
        crudos de la URL/body sin pasar antes por _consultar_pago_mp).

        Búsqueda del Pago local con dos niveles de fallback, igual que la
        cátedra: primero por mp_payment_id exacto; si no existe (primera
        vez que se ve este pago), se cae al último Pago del pedido (usando
        external_reference si está disponible, o pedido_id_hint).
        """
        mp_payment_id = int(mp_info["id"])
        external_reference = mp_info.get("external_reference")
        mp_status = mp_info.get("status")
        mp_status_detail = mp_info.get("status_detail")
        mp_merchant_order_id = (mp_info.get("order") or {}).get("id")

        nuevo_estado = self._mapear_estado_mp(mp_status)

        with PagoUnitofWork(self._session) as uow:
            pago = uow.pagos.get_by_mp_payment_id(mp_payment_id)

            if not pago and external_reference:
                pago = uow.pagos.get_by_external_reference(external_reference)

            if not pago and pedido_id_hint is not None:
                pago = uow.pagos.get_ultimo_by_pedido(pedido_id_hint)

            if not pago:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Pago not found in local DB",
                )

            # Idempotencia: una vez que el Pago deja de estar PENDIENTE,
            # se considera resuelto y no se vuelve a tocar.
            if pago.estado != EstadoPago.PENDIENTE:
                return PagoPublic.model_validate(pago)

            estado_anterior = pago.estado
            pago.mp_payment_id = mp_payment_id
            pago.mp_status = mp_status
            pago.mp_status_detail = mp_status_detail
            if mp_merchant_order_id is not None:
                pago.mp_merchant_order_id = int(mp_merchant_order_id)
            pago.estado = nuevo_estado
            uow.pagos.add(pago)

            # "Actualizar pedido": avanzar SOLO cuando corresponde.
            if nuevo_estado == EstadoPago.APROBADO:
                self._avanzar_pedido(
                    uow, pago.pedido_id, _ESTADO_PEDIDO_AL_APROBAR,
                    motivo=f"Pago {mp_payment_id} aprobado por MercadoPago",
                )
            elif nuevo_estado == EstadoPago.RECHAZADO:
                # No mueve el pedido: el usuario puede reintentar el pago
                # sobre el mismo pedido, que sigue PENDIENTE.
                logger.info(f"Pago {mp_payment_id} rechazado para pedido {pago.pedido_id}")
            elif nuevo_estado == EstadoPago.CANCELADO:
                self._avanzar_pedido(
                    uow, pago.pedido_id, _ESTADO_PEDIDO_AL_RECHAZAR,
                    motivo=f"Pago {mp_payment_id} cancelado/devuelto",
                )

            return PagoPublic.model_validate(pago)

    def _avanzar_pedido(self, uow: PagoUnitofWork, pedido_id: int, nuevo_estado_codigo: str, motivo: str) -> None:
        """
        Avanza el estado_codigo del Pedido y registra el historial,
        replicando la lógica que ya usa PedidoService.update() para no
        introducir un segundo camino de transición de estados.

        Nota sobre la FSM: PedidoService.update() exige
        orden_nuevo - orden_actual == 1 (solo el siguiente estado
        correlativo). Acá replicamos esa regla para PENDIENTE->CONFIRMADO,
        pero permitimos CANCELADO desde cualquier estado no terminal, ya
        que un pago rechazado/devuelto debe poder cancelar el pedido sin
        importar en qué paso de la FSM esté.
        """
        pedido = uow.pedidos.get_by_id(pedido_id)
        if pedido is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"pedido con id={pedido_id} no encontrado",
            )

        if pedido.estado_codigo == nuevo_estado_codigo:
            return  # ya está en ese estado, no hay nada que hacer

        estado_actual = uow.estado_pedido.get_by_codigo(pedido.estado_codigo)
        estado_nuevo = uow.estado_pedido.get_by_codigo(nuevo_estado_codigo)

        if estado_actual is None or estado_nuevo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estado de pedido no encontrado al intentar avanzar la FSM",
            )

        if estado_actual.es_terminal:
            logger.warning(
                f"Se intentó mover el pedido {pedido_id} desde un estado "
                f"terminal ({pedido.estado_codigo}) hacia {nuevo_estado_codigo}. "
                f"Se ignora la transición."
            )
            return

        es_cancelacion = nuevo_estado_codigo == _ESTADO_PEDIDO_AL_RECHAZAR
        if not es_cancelacion and (estado_nuevo.orden - estado_actual.orden) != 1:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Transición de estado no permitida: "
                    f"{pedido.estado_codigo} -> {nuevo_estado_codigo}"
                ),
            )

        historial = HistorialEstadoPedido(
            pedido_id=pedido.id,
            estado_desde=pedido.estado_codigo,
            estado_hacia=nuevo_estado_codigo,
            usuario_id=None,  # transición disparada por el sistema, no por un usuario
            motivo=motivo,
        )
        uow.historial_estado_pedido.add(historial)

        pedido.estado_codigo = nuevo_estado_codigo
        uow.pedidos.add(pedido)

    # ---------- consultas ----------

    def get_by_id(self, pago_id: int) -> PagoPublic:
        with PagoUnitofWork(self._session) as uow:
            pago = self._get_or_404(uow, pago_id)
            return PagoPublic.model_validate(pago)

    def get_by_pedido_id(self, pedido_id: int) -> PagoList:
        with PagoUnitofWork(self._session) as uow:
            pagos = uow.pagos.get_by_pedido_id(pedido_id)

        return PagoList(
            data=[PagoPublic.model_validate(p) for p in pagos],
            total=len(pagos),
        )