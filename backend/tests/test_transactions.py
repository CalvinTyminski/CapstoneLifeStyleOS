
import uuid

import pytest
from sqlalchemy import event

from app.models.ledger import LedgerEntry
from tests.test_wallet import authenticated_client


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
