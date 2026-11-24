
import uuid
import pytest

from decimal import Decimal

from sqlalchemy import event
from sqlalchemy import select

from concurrent.futures import ThreadPoolExecutor

from tests.conftest import TestingSessionLocal
from tests.test_wallet import authenticated_client

from app.models.wallet import Wallet
from app.services.wallet_service import add_mock_deposit
from app.models.ledger import LedgerEntry



def test_failed_ledger_insert_rolls_back_balance(client):
    headers = authenticated_client(client)
    headers["Idempotency-Key"] = str(uuid.uuid4())

    def simulate_ledger_failure(
        mapper, connection, target
    ):
        raise RuntimeError("Simulated ledger failure")

    event.listen(
        LedgerEntry,
        "before_insert",
        simulate_ledger_failure,
    )

    try:
        with pytest.raises(
            RuntimeError,
            match="Simulated ledger failure",
        ):
            client.post(
                "/api/wallet/mock-deposits",
                json={"amount": "100.00"},
                headers=headers,
            )
    finally:
        event.remove(
            LedgerEntry,
            "before_insert",
            simulate_ledger_failure,
        )

    wallet_response = client.get(
        "/api/wallet",
        headers=headers,
    )

    assert wallet_response.status_code == 200
    assert wallet_response.json()["balance"] in (
        "0.00", 0, 0.0
    )

    history = client.get(
        "/api/wallet/transactions",
        headers=headers,
    )

    assert history.status_code == 200
    assert len(history.json()) == 0

def test_negative_deposit_rejected(client):
    headers = authenticated_client(client)
    headers["Idempotency-Key"] = str(uuid.uuid4())

    response = client.post(
        "/api/wallet/mock-deposits",
        json={"amount": "-50.00"},
        headers=headers,
    )

    assert response.status_code == 422

    wallet = client.get(
        "/api/wallet",
        headers=headers,
    )

    assert float(wallet.json()["balance"]) == 0.0


def test_excessive_deposit_rejected(client):
    headers = authenticated_client(client)
    headers["Idempotency-Key"] = str(uuid.uuid4())

    response = client.post(
        "/api/wallet/mock-deposits",
        json={"amount": "5000.00"},
        headers=headers,
    )

    assert response.status_code == 422

    wallet = client.get(
        "/api/wallet",
        headers=headers,
    )

    assert float(wallet.json()["balance"]) == 0.0

def test_concurrent_deposits(client):
    headers = authenticated_client(client)

    # Get the user ID from the authenticated endpoint.
    user_response = client.get(
        "/api/auth/me",
        headers=headers,
    )

    assert user_response.status_code == 200
    user_id = user_response.json()["id"]

    def make_deposit(key):
        # Each thread needs its own SQLAlchemy session.
        with TestingSessionLocal() as db:
            return add_mock_deposit(
                db=db,
                user_id=user_id,
                amount=Decimal("100.00"),
                idempotency_key=key,
            )

    keys = [
        str(uuid.uuid4()),
        str(uuid.uuid4()),
    ]

    # Submit both deposits concurrently.
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(
            executor.map(make_deposit, keys)
        )

    assert len(results) == 2
    assert all(
        result["already_processed"] is False
        for result in results
    )

    # Verify the committed database balance.
    with TestingSessionLocal() as db:
        wallet = db.execute(
            select(Wallet).where(
                Wallet.user_id == user_id
            )
        ).scalar_one()

        assert wallet.balance == Decimal("200.00")

    # Verify the history contains both transactions.
    history = client.get(
        "/api/wallet/transactions",
        headers=headers,
    )

    assert history.status_code == 200
    assert len(history.json()) == 2
