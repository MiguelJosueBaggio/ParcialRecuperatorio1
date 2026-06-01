from datetime import datetime, timezone
from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.RefreshToken.models import RefreshToken


class RefreshTokenRepository(BaseRepository[RefreshToken]):

    def __init__(self, session: Session) -> None:
        super().__init__(session, RefreshToken)

    def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        return self.session.exec(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        ).first()

    def get_activos_por_usuario(self, usuario_id: int) -> list[RefreshToken]:
        ahora = datetime.now(timezone.utc)
        return list(self.session.exec(
            select(RefreshToken)
            .where(RefreshToken.usuario_id == usuario_id)
            .where(RefreshToken.expires_at > ahora)
            .where(RefreshToken.revoked_at == None)
        ).all())

    def revocar_todos_del_usuario(self, usuario_id: int) -> int:
        ahora = datetime.now(timezone.utc)
        tokens = self.get_activos_por_usuario(usuario_id)
        for token in tokens:
            token.revoked_at = ahora
            self.session.add(token)
        self.session.flush()
        return len(tokens)

    def limpiar_expirados(self) -> int:
        ahora = datetime.now(timezone.utc)
        expirados = list(self.session.exec(
            select(RefreshToken).where(RefreshToken.expires_at < ahora)
        ).all())
        for token in expirados:
            self.session.delete(token)
        self.session.flush()
        return len(expirados)