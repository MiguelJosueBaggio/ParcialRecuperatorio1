from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.database import get_session
from app.modules.Rol.service import RolService
from app.modules.Rol.schemas import RolCreate, RolUpdate, RolPublic

router = APIRouter()


def get_rol_service(session: Session = Depends(get_session)) -> RolService:
    """Factory de dependencia: inyecta el servicio con su Session."""
    return RolService(session)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=list[RolPublic],
    summary="Listar todos los roles",
)
def list_roles(
    svc: RolService = Depends(get_rol_service),
) -> list[RolPublic]:
    return svc.get_all()


@router.get(
    "/usuarios/{usuario_id}",
    response_model=list[RolPublic],
    summary="Obtener todos los roles de un usuario",
)
def get_roles_de_usuario(
    usuario_id: int,
    svc: RolService = Depends(get_rol_service),
) -> list[RolPublic]:
    return svc.get_roles_de_usuario(usuario_id)


@router.get(
    "/{codigo}",
    response_model=RolPublic,
    summary="Obtener rol por código",
)
def get_rol(
    codigo: str,
    svc: RolService = Depends(get_rol_service),
) -> RolPublic:
    return svc.get_by_codigo(codigo)


@router.post(
    "/",
    response_model=RolPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un rol",
)
def create_rol(
    data: RolCreate,
    svc: RolService = Depends(get_rol_service),
) -> RolPublic:
    return svc.create(data)


@router.patch(
    "/{codigo}",
    response_model=RolPublic,
    summary="Actualización parcial de un rol",
)
def update_rol(
    codigo: str,
    data: RolUpdate,
    svc: RolService = Depends(get_rol_service),
) -> RolPublic:
    return svc.update(codigo, data)


@router.delete(
    "/{codigo}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un rol (delete físico)",
)
def delete_rol(
    codigo: str,
    svc: RolService = Depends(get_rol_service),
) -> None:
    svc.delete(codigo)


# ── Asignación de roles a usuarios ────────────────────────────────────────────

@router.post(
    "/{codigo}/usuarios/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Asignar un rol a un usuario",
)
def asignar_rol(
    codigo: str,
    usuario_id: int,
    svc: RolService = Depends(get_rol_service),
) -> None:
    svc.asignar_rol(usuario_id=usuario_id, rol_codigo=codigo)


@router.delete(
    "/{codigo}/usuarios/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Quitar un rol a un usuario",
)
def quitar_rol(
    codigo: str,
    usuario_id: int,
    svc: RolService = Depends(get_rol_service),
) -> None:
    svc.quitar_rol(usuario_id=usuario_id, rol_codigo=codigo)