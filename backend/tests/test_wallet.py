
import uuid


def authenticated_client(client):
    email = "wallet@example.com"
    password = "TestPassword123!"

    response = client.post(
        "/api/auth/register",
        json={
            "username": "walletuser",
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def test_new_wallet_starts_at_zero(client):
    headers = authenticated_client(client)

    response = client.get(
        "/api/wallet",
        headers=headers,
    )

    assert response.status_code == 200
    assert float(response.json()["balance"]) == 0.0


def test_mock_deposit_updates_balance(client):
    headers = authenticated_client(client)

    headers["Idempotency-Key"] = str(uuid.uuid4())

    response = client.post(
        "/api/wallet/mock-deposits",
        json={"amount": "100.00"},
        headers=headers,
    )

    assert response.status_code == 200
    assert float(response.json()["balance"]) == 100.0

    wallet_response = client.get(
        "/api/wallet",
        headers=headers,
    )

    assert float(wallet_response.json()["balance"]) == 100.0

    history_response = client.get(
        "/api/wallet/transactions",
        headers=headers,
    )

    assert history_response.status_code == 200

    transactions = history_response.json()

    assert len(transactions) == 1
    assert transactions[0]["event_type"] == "DEPOSIT"
    assert float(transactions[0]["amount"]) == 100.0


def test_duplicate_deposit_is_idempotent(client):
    headers = authenticated_client(client)

    headers["Idempotency-Key"] = str(uuid.uuid4())

    first = client.post(
        "/api/wallet/mock-deposits",
        json={"amount": "100.00"},
        headers=headers,
    )

    second = client.post(
        "/api/wallet/mock-deposits",
        json={"amount": "100.00"},
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

    wallet = client.get(
        "/api/wallet",
        headers=headers,
    )

    assert float(wallet.json()["balance"]) == 100.0

    history = client.get(
        "/api/wallet/transactions",
        headers=headers,
    )

    assert len(history.json()) == 1

