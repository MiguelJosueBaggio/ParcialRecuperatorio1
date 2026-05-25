from sqlmodel import Session
from app.core.database import engine  # era: from app.db import engine
from app.modules.EstadoPedido.models import EstadoPedidoModel

def seed_estado_pedido():

    estados = [
        EstadoPedidoModel(
            codigo="PENDIENTE",
            descripcion="Pedido creado",
            orden=1,
            es_terminal=False
        ),
        EstadoPedidoModel(
            codigo="CONFIRMADO",
            descripcion="Pedido confirmado",
            orden=2,
            es_terminal=False
        ),
        EstadoPedidoModel(
            codigo="EN_PREP",
            descripcion="Pedido en preparación",
            orden=3,
            es_terminal=False
        ),
        EstadoPedidoModel(
            codigo="EN_CAMINO",
            descripcion="Pedido en camino",
            orden=4,
            es_terminal=False
        ),
        EstadoPedidoModel(
            codigo="ENTREGADO",
            descripcion="Pedido entregado",
            orden=5,
            es_terminal=True
        ),
        EstadoPedidoModel(
            codigo="CANCELADO",
            descripcion="Pedido cancelado",
            orden=6,
            es_terminal=True
        ),
    ]

    with Session(engine) as session:
        for estado in estados:
            existente = session.get(
                EstadoPedidoModel,
                estado.codigo
            )

            if not existente:
                session.add(estado)

        session.commit()

    print("Seed EstadoPedido ejecutado.")