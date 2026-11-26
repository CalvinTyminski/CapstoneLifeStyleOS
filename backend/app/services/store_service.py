
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.wallet import Wallet
from app.models.ledger import LedgerEntry
from app.models.store_item import StoreItem
from app.models.purchase import Purchase


class StoreError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def purchase_item(
    db: Session,
    user_id: int,
    item_id: int,
    idempotency_key: str,
):
    try:
        # Lock this user's wallet to serialize purchases.
        wallet = db.execute(
            select(Wallet)
            .where(Wallet.user_id == user_id)
            .with_for_update()
        ).scalar_one_or_none()

        if wallet is None:
            raise StoreError("Wallet not found", 404)

        # Detect an already completed purchase.
        existing = db.execute(
            select(Purchase).where(
                Purchase.user_id == user_id,
                Purchase.idempotency_key == idempotency_key,
            )
        ).scalar_one_or_none()

        if existing is not None:
            if existing.item_id != item_id:
                raise StoreError(
                    "Idempotency key used for another item",
                    409,
                )

            result = {
                "purchase_id": existing.id,
                "transaction_id": existing.transaction_id,
                "item_id": existing.item_id,
                "amount_paid": existing.amount_paid,
                "balance": wallet.balance,
                "already_processed": True,
            }

            db.commit()
            return result

        # Determine the price on the server.
        item = db.get(StoreItem, item_id)

        if item is None or not item.is_active:
            raise StoreError("Item not available", 404)

        if wallet.balance < item.price:
            raise StoreError("Insufficient funds", 409)

        # All changes occur in one database transaction.
        wallet.balance -= item.price

        transaction_id = uuid4()

        ledger_entry = LedgerEntry(
            wallet_id=wallet.id,
            transaction_id=transaction_id,
            event_type="PURCHASE",
            amount=-item.price,
        )
        db.add(ledger_entry)

        purchase = Purchase(
            user_id=user_id,
            wallet_id=wallet.id,
            item_id=item.id,
            transaction_id=transaction_id,
            idempotency_key=idempotency_key,
            amount_paid=item.price,
        )
        db.add(purchase)

        db.flush()

        result = {
            "purchase_id": purchase.id,
            "transaction_id": transaction_id,
            "item_id": item.id,
            "amount_paid": item.price,
            "balance": wallet.balance,
            "already_processed": False,
        }

        db.commit()
        return result

    except Exception:
        db.rollback()
        raise
