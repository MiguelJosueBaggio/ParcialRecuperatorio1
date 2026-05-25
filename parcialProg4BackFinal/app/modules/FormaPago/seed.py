from sqlmodel import Session, select
from app.modules.FormaPago.models import FormaPago


def seed_forma_pago(session: Session):

    formas_pago = [

        (
            "MERCADOPAGO",
            "Checkout API · CardPayment SDK",
            True
        ),

        (
            "EFECTIVO",
            "Retiro en local (direccion_id=NULL)",
            True
        ),

        (
            "TRANSFERENCIA",
            "Bancaria",
            False
        )

    ]

    for codigo, descripcion, habilitado in formas_pago:

        existing = session.exec(
            select(FormaPago).where(
                FormaPago.codigo == codigo
            )
        ).first()

        if existing:
            continue

        session.add(
            FormaPago(
                codigo=codigo,
                descripcion=descripcion,
                habilitado=habilitado
            )
        )

    session.commit()