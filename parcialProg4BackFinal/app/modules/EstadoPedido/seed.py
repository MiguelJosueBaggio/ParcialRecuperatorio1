from sqlmodel import Session, select
from app.modules.EstadoPedido.models import EstadoPedidoModel


def seed_estado_pedido(session: Session):
    estados = [
        ("PENDIENTE", "Pedido creado", 1, False),
        ("CONFIRMADO", "Pedido confirmado", 2, False),
        ("EN_PREP", "Pedido en preparación", 3, False),
        ("EN_CAMINO", "Pedido en camino", 4, False),
        ("ENTREGADO", "Pedido entregado", 5, True),
        ("CANCELADO", "Pedido cancelado", 6, True),
    ]

    for codigo, desc, orden, terminal in estados:

        existing = session.exec(
            select(EstadoPedidoModel).where(EstadoPedidoModel.codigo == codigo)
        ).first()

        if existing:
            continue

        session.add(
            EstadoPedidoModel(
                codigo=codigo,
                descripcion=desc,
                orden=orden,
                es_terminal=terminal
            )
        )

    session.commit()