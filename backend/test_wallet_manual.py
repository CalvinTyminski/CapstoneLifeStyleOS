from decimal import Decimal
from uuid import uuid4

from pwdlib import PasswordHash
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.user import User
from app.models.wallet import Wallet
from app.models.ledger import LedgerEntry
from app.services.wallet_service import deposit_mock_funds


def main():
    # Generate a new test account for this run
    suffix = uuid4().hex[:10]

    with SessionLocal() as db:
        with db.begin():
            user = User(
                username=f"wallet_test_{suffix}",
                email=f"wallet_{suffix}@example.invalid",
                password_hash=PasswordHash.recommended().hash(
                    uuid4().hex
                ),
            )
            db.add(user)
            db.flush()

            wallet = Wallet(user_id=user.id)
            db.add(wallet)

            user_id = user.id

    # Deposit simulated funds
    with SessionLocal() as db:
        result = deposit_mock_funds(
            db=db,
            user_id=user_id,
            amount=Decimal("100.00"),
        )

        print("Deposit result:", result)

    # Confirm balance and ledger match
    with SessionLocal() as db:
        wallet = db.execute(
            select(Wallet).where(
                Wallet.user_id == user_id
            )
        ).scalar_one()

        entries = db.execute(
            select(LedgerEntry).where(
                LedgerEntry.wallet_id == wallet.id
            )
        ).scalars().all()

        assert wallet.balance == Decimal("100.00")
        assert len(entries) == 1
        assert entries[0].amount == Decimal("100.00")

        print("Balance:", wallet.balance)
        print("Ledger entries:", len(entries))
        print("Wallet test passed!")


if __name__ == "__main__":
    main()