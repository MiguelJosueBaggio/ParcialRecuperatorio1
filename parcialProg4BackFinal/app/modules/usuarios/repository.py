"""
Repositorio de Usuario.

Acceso a BD: queries sin lógica de negocio.
Hereda de BaseRepository[Usuario] y agrega queries específicas.

Capa: Repository
Conoce a: Model (Usuario), Session
NO conoce a: Service, Router
"""

from sqlmodel import Session, select

from app.core.repository import BaseRepository
from app.modules.usuarios.model import Usuario


class UsuarioRepository(BaseRepository[Usuario]):

    def __init__(self, session: Session) -> None:
        super().__init__(session, Usuario)  # orden correcto: session primero, luego model

    def get_by_email(self, email: str) -> Usuario | None:
        return self.session.exec(
            select(Usuario).where(Usuario.email == email)
        ).first()

    def get_active(self, offset: int = 0, limit: int = 20) -> list[Usuario]:
        return list(self.session.exec(
            select(Usuario)
            .where(Usuario.deleted_at == None)
            .offset(offset)
            .limit(limit)
        ).all())