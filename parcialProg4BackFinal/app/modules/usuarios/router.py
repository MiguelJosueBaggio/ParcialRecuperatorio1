"""
Router de autenticación y gestión de usuarios.

HTTP puro: parsear request, validar schema Pydantic, delegar al Service,
serializar response con response_model. No contiene lógica de negocio.

Capa: Router
Conoce a: Service (vía UoW)
NO conoce a: Repository, Model (solo esquemas Pydantic para response_model)

Regla de imports:
    Router → Service → UoW → Repository → Model
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.core.unit_of_work import UnitOfWork, get_uow
from app.core.deps import get_current_active_user
from app.modules.usuarios.schemas import UserCreate, UserPublic
from app.modules.usuarios.service import UsuarioService
from app.modules.RefreshToken.service import RefreshTokenService

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


# ── Registro ──────────────────────────────────────────────────────────────────

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserCreate,
    uow: Annotated[UnitOfWork, Depends(get_uow)],
):
    with uow:
        service = UsuarioService(uow)
        return service.register(user_in)


# ── Login ─────────────────────────────────────────────────────────────────────
# OAuth2PasswordRequestForm usa "username" por protocolo,
# pero nosotros lo tratamos como email internamente.

@router.post("/token")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    uow: Annotated[UnitOfWork, Depends(get_uow)],
    response: Response,
):
    with uow:
        service = UsuarioService(uow)
        token = service.authenticate(form_data.username, form_data.password)
        usuario = uow.usuarios.get_by_email(form_data.username)
        rt_service = RefreshTokenService(uow)
        refresh_token_raw = rt_service.crear_refresh_token(usuario.id)

    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
        max_age=token.expires_in,
        samesite="lax",
        secure=False,  # True en producción con HTTPS
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token_raw,
        httponly=True,
        max_age=60 * 60 * 24 * 30,
        samesite="lax",
        secure=False,
        path="/api/v1/auth/refresh",
    )
    return {"mensaje": "Login exitoso. Sesión iniciada."}

# ── Refresh Token ─────────────────────────────────────────────────────────────

@router.post("/refresh")
def refresh(
    request: Request,
    uow: Annotated[UnitOfWork, Depends(get_uow)],
    response: Response,
):
    refresh_token_raw = request.cookies.get("refresh_token")

    if not refresh_token_raw:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No hay refresh token — iniciá sesión nuevamente",
        )

    with uow:
        rt_service = RefreshTokenService(uow)
        nuevo_token = rt_service.renovar_access_token(refresh_token_raw)

    response.set_cookie(
        key="access_token",
        value=nuevo_token.access_token,
        httponly=True,
        max_age=nuevo_token.expires_in,
        samesite="lax",
        secure=False,
    )
    return {"mensaje": "Access token renovado exitosamente"}

# ── Logout ────────────────────────────────────────────────────────────────────

router.post("/logout")
def logout(
    request: Request,
    uow: Annotated[UnitOfWork, Depends(get_uow)],
    response: Response,
):
    refresh_token_raw = request.cookies.get("refresh_token")

    if refresh_token_raw:
        with uow:
            rt_service = RefreshTokenService(uow)
            rt_service.revocar_token(refresh_token_raw)

    response.delete_cookie(key="access_token", httponly=True, samesite="lax")
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        samesite="lax",
        path="/api/v1/auth/refresh",
    )
    return {"mensaje": "Sesión cerrada exitosamente"}


# ── /me ───────────────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserPublic)
def read_me(
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
):
    return current_user
