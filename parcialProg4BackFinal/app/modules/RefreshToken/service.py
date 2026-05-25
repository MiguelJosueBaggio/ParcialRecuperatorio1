import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status

from app.core.security import create_access_token
from app.core.unit_of_work import UnitOfWork
from app.modules.RefreshToken.models import RefreshToken
from app.modules.usuarios.schemas import Token

REFRESH_TOKEN_EXPIRE_DAYS = 30


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class RefreshTokenService:

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    def crear_refresh_token(self, usuario_id: int) -> str:
        token_raw = secrets.token_hex(64)
        token_hash = _hash_token(token_raw)
        expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        refresh = RefreshToken(
            usuario_id=usuario_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.uow.refresh_tokens.add(refresh)
        return token_raw

    def renovar_access_token(self, token_raw: str) -> Token:
        token_hash = _hash_token(token_raw)
        refresh = self.uow.refresh_tokens.get_by_hash(token_hash)

        if not refresh:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido")

        if refresh.revoked_at is not None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revocado")

        if refresh.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expirado")

        nuevo_access = create_access_token(data={"sub": str(refresh.usuario_id)})

        from app.core.config import settings
        return Token(
            access_token=nuevo_access,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    def revocar_token(self, token_raw: str) -> None:
        token_hash = _hash_token(token_raw)
        refresh = self.uow.refresh_tokens.get_by_hash(token_hash)
        if refresh and refresh.revoked_at is None:
            refresh.revoked_at = datetime.now(timezone.utc)
            self.uow.refresh_tokens.add(refresh)

    def revocar_todos(self, usuario_id: int) -> None:
        self.uow.refresh_tokens.revocar_todos_del_usuario(usuario_id)