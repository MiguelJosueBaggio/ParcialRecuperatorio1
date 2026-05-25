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

from fastapi import APIRouter, Depends, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.core.database import get_session
from app.core.deps import get_current_active_user

from app.modules.usuarios.schemas import (
    UserCreate,
    UserPublic
)

from app.modules.usuarios.service import UsuarioService


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"]
)


# ---------- REGISTER ----------

@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_in: UserCreate,

    session: Annotated[
        Session,
        Depends(get_session)
    ]
):

    service = UsuarioService(session)

    return service.register(user_in)


# ---------- LOGIN ----------

@router.post("/token")
def login(

    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends()
    ],

    session: Annotated[
        Session,
        Depends(get_session)
    ],

    response: Response
):

    service = UsuarioService(session)

    token = service.authenticate(
        form_data.username,
        form_data.password
    )

    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
        max_age=token.expires_in,
        samesite="lax",
        secure=False
    )

    return {
        "mensaje":
        "Login exitoso"
    }


# ---------- LOGOUT ----------

@router.post("/logout")
def logout(
    response: Response
):

    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
        secure=False
    )

    return {
        "mensaje":
        "Sesión cerrada"
    }


# ---------- ME ----------

@router.get(
    "/me",
    response_model=UserPublic
)
def read_me(

    current_user: Annotated[
        UserPublic,
        Depends(get_current_active_user)
    ]
):

    return current_user