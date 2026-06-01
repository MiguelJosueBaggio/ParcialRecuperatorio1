from sqlmodel import Session, select
from app.modules.Rol.models import Rol


def seed_roles(session: Session):

    roles = [
        ("ADMIN", "Administrador", "Acceso total sin restricciones"),
        ("STOCK", "Operador Stock", "Actualiza stock y disponible"),
        ("PEDIDOS", "Operador Pedidos", "Avanza estados CONFIRMADO→ENTREGADO"),
        ("CLIENT", "Cliente", "Opera solo sus propios datos"),
    ]

    for codigo, nombre, desc in roles:

        existing = session.exec(
            select(Rol).where(Rol.codigo == codigo)
        ).first()

        if existing:
            continue

        session.add(
            Rol(
                codigo=codigo,
                nombre=nombre,
                descripcion=desc
            )
        )

    session.commit()