from datetime import datetime, timezone
from sqlmodel import Session
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)
from app.modules.usuarios.unit_of_work import UsuarioUnitofWork

from app.modules.usuarios.model import Usuario
from app.modules.usuarios.schemas import (
    UserCreate,
    UserPublic,
    Token
)

from app.modules.Direccion_Entrega.models import Direccion
from app.modules.Direccion_Entrega.schema import DireccionUpdate


class UsuarioService:

    def __init__(self, session: Session):
        self._session = session

    # ---------------- HELPERS ----------------

    def _get_or_404(self, uow, user_id: int) -> Usuario:

        usuario = uow.usuarios.get_by_id(user_id)

        if not usuario:
            raise HTTPException(
                status_code=404,
                detail=f"Usuario {user_id} no encontrado"
            )

        return usuario

    # ---------------- REGISTER ----------------

    def register(self, user_in: UserCreate) -> UserPublic:

        with UsuarioUnitofWork(self._session) as uow:

            if uow.usuarios.get_by_email(user_in.email):
                raise HTTPException(
                    status_code=409,
                    detail="El email ya está registrado"
                )

            usuario = Usuario(
                nombre=user_in.nombre,
                apellido=user_in.apellido,
                email=user_in.email,
                celular=user_in.celular,
                password_hash=hash_password(user_in.password)
            )

            usuario.direcciones = []

            for direccion in user_in.direcciones:

                nueva_direccion = Direccion(
                    alias=direccion.alias,
                    linea1=direccion.linea1,
                    linea2=direccion.linea2,
                    ciudad=direccion.ciudad,
                    provincia=direccion.provincia,
                    codigo_postal=direccion.codigo_postal,
                    es_principal=direccion.es_principal
                )

                # NO pongas usuario_id manualmente
                # SQLAlchemy lo hace por la relación

                usuario.direcciones.append(
                    nueva_direccion
                )

            creado = uow.usuarios.add(usuario)

            uow.commit()

            return UserPublic.model_validate(creado)

    # ---------------- LOGIN ----------------

    def authenticate(
        self,
        email:str,
        password:str
    ) -> Token:

        with UsuarioUnitofWork(self._session) as uow:

            user = uow.usuarios.get_by_email(email)

            if not user or not verify_password(
                password,
                user.password_hash
            ):
                raise HTTPException(
                    status_code=401,
                    detail="Credenciales incorrectas",
                    headers={
                        "WWW-Authenticate":"Bearer"
                    }
                )

            if user.deleted_at is not None:

                raise HTTPException(
                    status_code=400,
                    detail="Cuenta desactivada"
                )

            access_token = create_access_token(
                data={
                    "sub":str(user.id),
                    "email":user.email
                }
            )

            return Token(
                access_token=access_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )

    # ---------------- LISTAR ----------------

    def list_all(
        self,
        offset:int=0,
        limit:int=20
    ) -> list[UserPublic]:

        with UsuarioUnitofWork(self._session) as uow:

            usuarios = uow.usuarios.get_active(
                offset=offset,
                limit=limit
            )

            return [
                UserPublic.model_validate(u)
                for u in usuarios
            ]

    # ---------------- UPDATE DIRECCIONES ----------------

    def update_direcciones(
        self,
        usuario_id:int,
        data:list[DireccionUpdate]
    ) -> UserPublic:

        with UsuarioUnitofWork(self._session) as uow:

            usuario = self._get_or_404(
                uow,
                usuario_id
            )

            for direccion_data in data:

                direccion = next(
                    (
                        d for d in usuario.direcciones
                        if d.id == direccion_data.id
                    ),
                    None
                )

                if not direccion:

                    raise HTTPException(
                        status_code=404,
                        detail=f"Direccion {direccion_data.id} no encontrada"
                    )

                update_data = direccion_data.model_dump(
                    exclude_unset=True
                )

                update_data.pop(
                    "id",
                    None
                )

                for campo, valor in update_data.items():

                    setattr(
                        direccion,
                        campo,
                        valor
                    )

            uow.commit()

            uow.session.refresh(usuario)

            return UserPublic.model_validate(
                usuario
            )

    # ---------------- SOFT DELETE ----------------

    def soft_delete(
        self,
        user_id:int
    ):

        with UsuarioUnitofWork(self._session) as uow:

            usuario = self._get_or_404(
                uow,
                user_id
            )

            usuario.deleted_at = datetime.now(
                timezone.utc
            )

            uow.commit()