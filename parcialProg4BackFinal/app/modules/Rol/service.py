from fastapi import HTTPException, status
from sqlmodel import Session

from app.modules.Rol.models import Rol
from app.modules.Rol.schemas import RolCreate, RolUpdate, RolPublic
from app.modules.Rol.unit_of_work import RolUnitOfWork


class RolService:

    def __init__(self, session: Session) -> None:
        self._session = session

    # ── Helpers privados ──────────────────────────────────────────────────────

    def _get_or_404(self, uow: RolUnitOfWork, codigo: str) -> Rol:
        rol = uow.roles.get_by_codigo(codigo)
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rol con codigo='{codigo}' no encontrado",
            )
        return rol

    def _assert_codigo_unico(self, uow: RolUnitOfWork, codigo: str) -> None:
        if uow.roles.get_by_codigo(codigo):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un rol con codigo='{codigo}'",
            )

    def _assert_nombre_unico(self, uow: RolUnitOfWork, nombre: str) -> None:
        if uow.roles.get_by_nombre(nombre):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un rol con nombre='{nombre}'",
            )

    # ── Operaciones ───────────────────────────────────────────────────────────

    def get_all(self) -> list[RolPublic]:
        with RolUnitOfWork(self._session) as uow:
            roles = uow.roles.get_all()
            return [RolPublic.model_validate(r) for r in roles]

    def get_by_codigo(self, codigo: str) -> RolPublic:
        with RolUnitOfWork(self._session) as uow:
            rol = self._get_or_404(uow, codigo)
            return RolPublic.model_validate(rol)

    def create(self, data: RolCreate) -> RolPublic:
        with RolUnitOfWork(self._session) as uow:
            self._assert_codigo_unico(uow, data.codigo)
            self._assert_nombre_unico(uow, data.nombre)
            rol = Rol.model_validate(data)
            uow.roles.add(rol)
            return RolPublic.model_validate(rol)

    def update(self, codigo: str, data: RolUpdate) -> RolPublic:
        with RolUnitOfWork(self._session) as uow:
            rol = self._get_or_404(uow, codigo)

            if data.nombre is not None and data.nombre != rol.nombre:
                self._assert_nombre_unico(uow, data.nombre)

            patch = data.model_dump(exclude_unset=True)
            for field, value in patch.items():
                setattr(rol, field, value)

            uow.roles.add(rol)
            return RolPublic.model_validate(rol)

    def delete(self, codigo: str) -> None:
        """
        Rol usa delete físico — no tiene is_active ni deleted_at.
        Es un catálogo semántico que no debería eliminarse en producción,
        pero se expone para el CRUD completo.
        """
        with RolUnitOfWork(self._session) as uow:
            rol = self._get_or_404(uow, codigo)
            uow.roles.delete(rol)

    # ── Asignación de roles a usuarios ────────────────────────────────────────

    def asignar_rol(self, usuario_id: int, rol_codigo: str, asignado_por_id: int | None = None) -> None:
        with RolUnitOfWork(self._session) as uow:
            self._get_or_404(uow, rol_codigo)  # valida que el rol exista
            uow.roles.asignar_rol(usuario_id, rol_codigo, asignado_por_id)

    def quitar_rol(self, usuario_id: int, rol_codigo: str) -> None:
        with RolUnitOfWork(self._session) as uow:
            self._get_or_404(uow, rol_codigo)  # valida que el rol exista
            uow.roles.quitar_rol(usuario_id, rol_codigo)

    def get_roles_de_usuario(self, usuario_id: int) -> list[RolPublic]:
        with RolUnitOfWork(self._session) as uow:
            roles = uow.roles.get_roles_de_usuario(usuario_id)
            return [RolPublic.model_validate(r) for r in roles]