
def test_register_user(client):
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 201
    assert response.json()["username"] == "testuser"
    assert response.json()["email"] == "test@example.com"


def test_duplicate_registration(client):
    user = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123!",
    }

    first_response = client.post(
        "/api/auth/register", json=user
    )

    assert first_response.status_code == 201

    user["username"] = "anotheruser"

    second_response = client.post(
        "/api/auth/register", json=user
    )

    assert second_response.status_code == 409


def test_login_returns_token(client):
    client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123!",
        },
    )

    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
