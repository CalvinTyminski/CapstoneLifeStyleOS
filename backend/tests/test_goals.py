
from datetime import date, timedelta
from decimal import Decimal

from tests.test_wallet import authenticated_client


def create_test_goal(client, headers):
    response = client.post(
        "/api/goals",
        headers=headers,
        json={
            "name": "Workout for 30 minutes",
            "type": "FITNESS",
            "start_date": date.today().isoformat(),
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_create_goal(client):
    headers = authenticated_client(client)
    goal_id = create_test_goal(client, headers)

    response = client.get("/api/goals", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == goal_id
    assert response.json()[0]["completed"] is False


def test_goal_completion_awards_coins(client):
    headers = authenticated_client(client)
    goal_id = create_test_goal(client, headers)

    response = client.post(
        f"/api/goals/{goal_id}/complete",
        headers=headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["already_completed"] is False

    wallet = client.get("/api/wallet", headers=headers)

    assert Decimal(str(wallet.json()["balance"])) == Decimal("50.00")

    history = client.get(
        "/api/wallet/transactions",
        headers=headers,
    ).json()

    assert len(history) == 1
    assert history[0]["event_type"] == "REWARD"


def test_duplicate_goal_completion(client):
    headers = authenticated_client(client)
    goal_id = create_test_goal(client, headers)

    first = client.post(
        f"/api/goals/{goal_id}/complete",
        headers=headers,
    )
    second = client.post(
        f"/api/goals/{goal_id}/complete",
        headers=headers,
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["already_completed"] is False
    assert second.json()["already_completed"] is True

    wallet = client.get("/api/wallet", headers=headers)

    assert Decimal(str(wallet.json()["balance"])) == Decimal("50.00")


def test_expired_goal_cannot_be_rewarded(client):
    headers = authenticated_client(client)

    yesterday = date.today() - timedelta(days=1)
    last_week = date.today() - timedelta(days=7)

    goal = client.post(
        "/api/goals",
        headers=headers,
        json={
            "name": "Expired goal",
            "type": "HABIT",
            "start_date": last_week.isoformat(),
            "end_date": yesterday.isoformat(),
        },
    )

    assert goal.status_code == 201

    response = client.post(
        f"/api/goals/{goal.json()['id']}/complete",
        headers=headers,
    )

    assert response.status_code == 409

    wallet = client.get("/api/wallet", headers=headers)
    assert Decimal(str(wallet.json()["balance"])) == Decimal("0.00")
