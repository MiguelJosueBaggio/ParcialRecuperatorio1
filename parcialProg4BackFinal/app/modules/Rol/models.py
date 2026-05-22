from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func

if TYPE_CHECKING:
    from app.modules.usuarios.model import Usuario


# ── Tabla intermedia Usuario <-> Rol ──────────────────────────────────────────
class UsuarioRol(SQLModel, table=True):
    __tablename__ = "usuario_rol"

    # PK compuesta
    usuario_id: int = Field(foreign_key="usuario.id", primary_key=True)
    rol_codigo: str = Field(foreign_key="rol.codigo", primary_key=True)

    # Atributos
    asignado_por_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    expires_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now()),
    )


# ── Rol ───────────────────────────────────────────────────────────────────────
class Rol(SQLModel, table=True):
    __tablename__ = "rol"

    # PK semántica — el código es legible en el JWT payload (ej: "ADMIN")
    codigo: str = Field(primary_key=True, max_length=20)

    # Atributos
    nombre: str = Field(unique=True, max_length=50)
    descripcion: Optional[str] = None