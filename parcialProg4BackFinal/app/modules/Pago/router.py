import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.core.database import get_session
from app.core.config import settings
from app.core.deps import get_current_active_user
from app.modules.usuarios.schemas import UserPublic

from app.modules.Pago.service import PagoService
from app.modules.Pago.schemas import (
    CrearPreferenciaRequest,
    CrearPreferenciaResponse,
    ConfirmarPagoRequest,
    PagoPublic,
    PagoList,
)

logger = logging.getLogger("app.modules.Pago.router")

router = APIRouter()


def get_pago_service(session: Session = Depends(get_session)) -> PagoService:
    """Factory de dependencia: inyecta el servicio con su Session."""
    return PagoService(session)


@router.post(
    "/preferencia",
    response_model=CrearPreferenciaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear preferencia de pago (Checkout Pro)",
)
def crear_preferencia(
    data: CrearPreferenciaRequest,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
    svc: PagoService = Depends(get_pago_service),
) -> CrearPreferenciaResponse:
    """
    Paso 1 y 2 del flujo: 'Crear pedido -> solicitar preferencia'.
    Requiere usuario autenticado. Devuelve el init_point al que el
    frontend debe redirigir para que el usuario complete el pago.
    """
    return svc.crear_preferencia_para_pedido(data.pedido_id)


@router.get(
    "/redirect/{pedido_id}/{status_pago}",
    summary="Puente entre el back_url público de MP y el frontend real",
)
async def redirect_after_pago(pedido_id: int, status_pago: str, request: Request):
    """
    MercadoPago exige que las back_urls sean direcciones públicas
    (en desarrollo, la URL de ngrok del backend) — no puede redirigir
    directo a un frontend en localhost, que no es accesible desde internet.

    Este endpoint es ese punto público intermedio: recibe la vuelta de MP
    y reenvía al usuario al frontend real (settings.FRONTEND_URL), con los
    mismos query params que haya mandado MP (payment_id, status, etc.)
    para que el frontend pueda usarlos al llamar a /pagos/confirm.
    """
    frontend_url = settings.FRONTEND_URL or "http://localhost:5173"
    qs = request.query_params
    url = f"{frontend_url}/orders/{pedido_id}/{status_pago}"
    if qs:
        url += f"?{qs}"
    return RedirectResponse(url=url)


@router.post(
    "/confirm",
    response_model=PagoPublic,
    summary="Confirmar pago (llamado por el frontend tras volver del checkout)",
)
def confirm_payment(
    data: ConfirmarPagoRequest,
    svc: PagoService = Depends(get_pago_service),
) -> PagoPublic:
    """
    El frontend llama esto después de que /redirect lo trajo de vuelta.
    payment_id es opcional: si no vino en la URL de MP, el service busca
    el último Pago registrado para ese pedido como fallback.

    Endpoint público (no requiere sesión propia obligatoriamente, ya que
    el usuario puede volver de MP sin la cookie en algunos flujos) — ajustar
    a Depends(get_current_active_user) si tu cátedra exige que sea privado.
    """
    return svc.confirmar_pago(data.pedido_id, data.payment_id)


@router.post(
    "/webhook",
    summary="Notificación asíncrona (webhook IPN) de MercadoPago",
)
async def webhook_mercadopago(
    request: Request,
    svc: PagoService = Depends(get_pago_service),
):
    """
    Es el respaldo cuando el usuario cierra el navegador antes de volver.

    Regla de oro: SIEMPRE responde 200 OK, incluso si algo falla
    internamente. MercadoPago bloquea (deja de notificar) a quien
    responde con errores. Los reintentos/errores se manejan acá adentro,
    nunca devolviendo un status code distinto de 200 a MP.

    MercadoPago puede mandar el body como JSON o como form-urlencoded
    según el tipo de notificación, así que se soportan ambos formatos.
    """
    try:
        query_params = dict(request.query_params)
        if request.headers.get("content-type", "").startswith("application/json"):
            data = await request.json()
        else:
            data = dict(await request.form())

        resultado = svc.procesar_webhook(data, query_params=query_params)
        return resultado

    except Exception as exc:
        logger.exception(f"Error procesando webhook de MercadoPago: {exc}")
        return {"status": "error", "reason": str(exc)}


@router.get(
    "/{pago_id}",
    response_model=PagoPublic,
    summary="Obtener pago por ID",
)
def get_pago(
    pago_id: int,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
    svc: PagoService = Depends(get_pago_service),
) -> PagoPublic:
    return svc.get_by_id(pago_id)


@router.get(
    "/pedido/{pedido_id}",
    response_model=PagoList,
    summary="Listar pagos asociados a un pedido",
)
def get_pagos_de_pedido(
    pedido_id: int,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
    svc: PagoService = Depends(get_pago_service),
) -> PagoList:
    return svc.get_by_pedido_id(pedido_id)