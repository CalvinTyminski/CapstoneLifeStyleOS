
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select

from app.models.store_item import StoreItem
from app.models.purchase import Purchase
from tests.conftest import TestingSessionLocal
from tests.test_wallet import authenticated_client


def make_store_item():
    with TestingSessionLocal() as db:
        item = StoreItem(
            name=f"Test Item {uuid4().hex[:8]}",
            description="Test purchase item",
            price=Decimal("150.00"),
            category="City Upgrade",
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item.id


def test_successful_purchase(client):
    headers = authenticated_client(client)
    item_id = make_store_item()

    headers["Idempotency-Key"] = str(uuid4())

    deposit = client.post(
        "/api/wallet/mock-deposits",
        json={"amount": "500.00"},
        headers=headers,
    )
    assert deposit.status_code == 200

    headers["Idempotency-Key"] = str(uuid4())

    purchase = client.post(
        "/api/store/purchases",
        json={"item_id": item_id},
        headers=headers,
    )

    assert purchase.status_code == 200, purchase.text
    assert Decimal(str(purchase.json()["balance"])) == Decimal("350.00")

    wallet = client.get("/api/wallet", headers=headers)
    assert Decimal(str(wallet.json()["balance"])) == Decimal("350.00")

    history = client.get(
        "/api/wallet/transactions",
        headers=headers,
    ).json()

    assert len(history) == 2
    assert any(
        entry["event_type"] == "PURCHASE"
        and Decimal(str(entry["amount"])) == Decimal("-150.00")
        for entry in history
    )


def test_insufficient_funds(client):
    headers = authenticated_client(client)
    item_id = make_store_item()

    headers["Idempotency-Key"] = str(uuid4())

    response = client.post(
        "/api/store/purchases",
        json={"item_id": item_id},
        headers=headers,
    )

    assert response.status_code == 409

    wallet = client.get("/api/wallet", headers=headers)
    assert Decimal(str(wallet.json()["balance"])) == Decimal("0.00")

    purchases = client.get(
        "/api/store/purchases",
        headers=headers,
    )

    assert purchases.status_code == 200
    assert purchases.json() == []


def test_duplicate_purchase_not_charged_twice(client):
    headers = authenticated_client(client)
    item_id = make_store_item()

    headers["Idempotency-Key"] = str(uuid4())
    client.post(
        "/api/wallet/mock-deposits",
        json={"amount": "500.00"},
        headers=headers,
    )

    headers["Idempotency-Key"] = str(uuid4())

    first = client.post(
        "/api/store/purchases",
        json={"item_id": item_id},
        headers=headers,
    )

    second = client.post(
        "/api/store/purchases",
        json={"item_id": item_id},
        headers=headers,
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["already_processed"] is False
    assert second.json()["already_processed"] is True

    assert (
        first.json()["transaction_id"]
        == second.json()["transaction_id"]
    )

    wallet = client.get("/api/wallet", headers=headers)
    assert Decimal(str(wallet.json()["balance"])) == Decimal("350.00")

    purchases = client.get(
        "/api/store/purchases",
        headers=headers,
    )

    assert len(purchases.json()) == 1
