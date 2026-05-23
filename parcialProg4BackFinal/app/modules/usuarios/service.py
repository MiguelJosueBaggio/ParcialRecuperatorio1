"""
Service de Usuario — lógica de negocio.

Stateless, orquesta operaciones sobre los repositorios a través del UoW.
Lanza HTTPException. No hace commit/rollback directamente.

Capa: Service
Conoce a: UoW, Repository (indirectamente vía UoW)
NO conoce a: Router

Regla de imports:
    Router → Service → UoW → Repository → Model
"""

from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token
from app.core.unit_of_work import UnitOfWork
from app.modules.usuarios.model import Usuario
from app.modules.usuarios.schemas import UserCreate, Token, UserPublic


class UsuarioService:
    """Lógica de negocio para autenticación y gestión de usuarios."""

    """Lógica de negocio para autenticación y gestión de usuarios."""

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _get_or_404(self, user_id: int) -> Usuario:
        user = self.uow.usuarios.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con id={user_id} no encontrado",
            )
        return user

    # ── Operaciones ──────────────────────────────────────────────────────────

    def register(self, user_in: UserCreate) -> UserPublic:
        """Registra un nuevo usuario. El rol CLIENT se asigna automáticamente."""
        if self.uow.usuarios.get_by_email(user_in.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El email ya está registrado",
            )

        usuario = Usuario(
            nombre=user_in.nombre,
            apellido=user_in.apellido,
            email=user_in.email,
            celular=user_in.celular,
            password_hash=hash_password(user_in.password),
        )

        creado = self.uow.usuarios.add(usuario)
        return UserPublic.model_validate(creado)

    def authenticate(self, email: str, password: str) -> Token:
        """Autentica con email + password y retorna un Token JWT."""
        user = self.uow.usuarios.get_by_email(email)

        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cuenta de usuario desactivada",
            )

        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    def list_all(self, offset: int = 0, limit: int = 20) -> list[UserPublic]:
        """Lista todos los usuarios activos."""
        usuarios = self.uow.usuarios.get_active(offset=offset, limit=limit)
        return [UserPublic.model_validate(u) for u in usuarios]

    def soft_delete(self, user_id: int) -> None:
        """Soft delete de usuario (setea deleted_at)."""
        from datetime import datetime, timezone
        user = self._get_or_404(user_id)
        user.deleted_at = datetime.now(timezone.utc)
        self.uow.usuarios.add(user)
