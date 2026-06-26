from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.Pago.models import Pago


class PagoRepository(BaseRepository[Pago]):
    
    def __init__(self, session: Session) -> None:
        super().__init__(session, Pago)

    def get_by_external_reference(self, external_reference: str) -> Pago | None:
        statement = select(Pago).where(
            Pago.external_reference == external_reference
        )
        return self.session.exec(statement).first()

    def get_by_mp_payment_id(self, mp_payment_id: int) -> Pago | None:
        statement = select(Pago).where(Pago.mp_payment_id == mp_payment_id)
        return self.session.exec(statement).first()

    def get_by_idempotency_key(self, idempotency_key: str) -> Pago | None:
        statement = select(Pago).where(Pago.idempotency_key == idempotency_key)
        return self.session.exec(statement).first()

    def get_by_pedido_id(self, pedido_id: int) -> list[Pago]:
        statement = select(Pago).where(Pago.pedido_id == pedido_id)
        return list(self.session.exec(statement).all())