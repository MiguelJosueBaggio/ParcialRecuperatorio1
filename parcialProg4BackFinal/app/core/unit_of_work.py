from typing import Generator, Annotated

from fastapi import Depends
from sqlmodel import Session

from app.core.database import get_session


class UnitOfWork:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._init_repos()

    def _init_repos(self) -> None:
        from app.modules.usuarios.repository import UsuarioRepository
        from app.modules.RefreshToken.repository import RefreshTokenRepository
        self.usuarios = UsuarioRepository(self._session)
        self.refresh_tokens = RefreshTokenRepository(self._session)

    def __enter__(self) -> "UnitOfWork":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is None:
            self._session.commit()
        else:
            self._session.rollback()

    def commit(self) -> None:
        self._session.commit()

    def rollsback(self) -> None:
        self._session.rollback()


def get_uow(
    session: Annotated[Session, Depends(get_session)],
) -> Generator[UnitOfWork, None, None]:
    yield UnitOfWork(session)