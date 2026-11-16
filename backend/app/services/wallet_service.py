from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.wallet import Wallet
from app.models.ledger import LedgerEntry


def deposit_mock_funds(
    db: Session,
    user_id: int,
    amount: Decimal,
):
    # Validate the amount
    if (
        not amount.is_finite()
        or amount != amount.quantize(Decimal("0.01"))
        or amount <= 0
        or amount > Decimal("1000.00")
    ):
        raise ValueError(
            "Deposit must be between 0.01 and 1000.00"
        )

    # Caller must provide a session with no active transaction
    with db.begin():

        # Lock the wallet to prevent concurrent balance updates
        wallet = db.execute(
            select(Wallet)
            .where(Wallet.user_id == user_id)
            .with_for_update()
        ).scalar_one_or_none()

        if wallet is None:
            raise ValueError("Wallet does not exist")

        # Update balance
        wallet.balance += amount

        # Record transaction
        entry = LedgerEntry(
            wallet_id=wallet.id,
            transaction_id=uuid4(),
            event_type="DEPOSIT",
            amount=amount,
        )

        db.add(entry)
        db.flush()

        result = {
            "transaction_id": str(entry.transaction_id),
            "amount": str(amount),
            "new_balance": str(wallet.balance),
        }

    return result


def add_mock_deposit(
    db: Session,
    user_id: int,
    amount: Decimal,
    idempotency_key: str,
):
    """
    Credit a wallet and record a ledger entry atomically.

    The caller supplies a request-scoped database session.
    This function owns the commit/rollback boundary.
    """

    try:
        # Lock the user's wallet before checking the request.
        wallet = db.execute(
            select(Wallet)
            .where(Wallet.user_id == user_id)
            .with_for_update()
        ).scalar_one_or_none()

        if wallet is None:
            raise ValueError("Wallet not found")

        # The same request must not credit funds twice.
        existing = db.execute(
            select(LedgerEntry).where(
                LedgerEntry.wallet_id == wallet.id,
                LedgerEntry.idempotency_key == idempotency_key,
            )
        ).scalar_one_or_none()

        if existing is not None:
            if (
                existing.event_type != "DEPOSIT"
                or existing.amount != amount
            ):
                raise ValueError(
                    "Idempotency key already used for "
                    "a different transaction"
                )

            result = {
                "transaction_id": existing.transaction_id,
                "amount": existing.amount,
                "balance": wallet.balance,
                "already_processed": True,
            }

            db.commit()
            return result

        wallet.balance += amount

        entry = LedgerEntry(
            wallet_id=wallet.id,
            transaction_id=uuid4(),
            event_type="DEPOSIT",
            amount=amount,
            idempotency_key=idempotency_key,
        )

        db.add(entry)
        db.flush()

        result = {
            "transaction_id": entry.transaction_id,
            "amount": amount,
            "balance": wallet.balance,
            "already_processed": False,
        }

        # Balance and ledger entry commit together.
        db.commit()
        return result

    except Exception:
        db.rollback()
        raise
