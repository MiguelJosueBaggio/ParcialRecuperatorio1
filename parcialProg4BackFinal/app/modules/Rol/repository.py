from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.Rol.models import Rol, UsuarioRol


class RolRepository(BaseRepository[Rol]):

    def __init__(self, session: Session) -> None:
        super().__init__(session, Rol)

    def get_by_codigo(self, codigo: str) -> Rol | None:
        return self.session.exec(
            select(Rol).where(Rol.codigo == codigo)
        ).first()

    def get_by_nombre(self, nombre: str) -> Rol | None:
        return self.session.exec(
            select(Rol).where(Rol.nombre == nombre)
        ).first()

    def get_roles_de_usuario(self, usuario_id: int) -> list[Rol]:
        """Devuelve todos los roles activos asignados a un usuario."""
        return list(
            self.session.exec(
                select(Rol)
                .join(UsuarioRol, UsuarioRol.rol_codigo == Rol.codigo)
                .where(UsuarioRol.usuario_id == usuario_id)
            ).all()
        )

    def asignar_rol(self, usuario_id: int, rol_codigo: str, asignado_por_id: int | None = None) -> UsuarioRol:
        """Asigna un rol a un usuario. Si ya lo tiene, no duplica."""
        existente = self.session.exec(
            select(UsuarioRol)
            .where(UsuarioRol.usuario_id == usuario_id)
            .where(UsuarioRol.rol_codigo == rol_codigo)
        ).first()

        if existente:
            return existente

        link = UsuarioRol(
            usuario_id=usuario_id,
            rol_codigo=rol_codigo,
            asignado_por_id=asignado_por_id,
        )
        self.session.add(link)
        self.session.flush()
        return link

    def count(self) -> int:
        """Sobreescribe el count() base que filtra por is_active — Rol no tiene ese campo y cambiarlo afectaria el comportamiento de la aplicación."""
        from sqlalchemy import func
        stmt = select(func.count()).select_from(Rol)
        return self.session.exec(stmt).one()

    def quitar_rol(self, usuario_id: int, rol_codigo: str) -> None:
        """Quita un rol de un usuario."""
        link = self.session.exec(
            select(UsuarioRol)
            .where(UsuarioRol.usuario_id == usuario_id)
            .where(UsuarioRol.rol_codigo == rol_codigo)
        ).first()

        if link:
            self.session.delete(link)
            self.session.flush()