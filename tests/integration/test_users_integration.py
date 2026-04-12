def test_create_user_success(client):
    response = client.post(
        "/users/register",
        json={
            "username": "rafael",
            "email": "rafael@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["username"] == "rafael"
    assert payload["email"] == "rafael@example.com"
    assert "password_hash" not in payload


def test_create_user_duplicate_username(client):
    body = {
        "username": "rafael",
        "email": "rafael@example.com",
        "password": "password123",
    }
    first_response = client.post("/users/register", json=body)
    assert first_response.status_code == 201

    duplicate_response = client.post(
        "/users/register",
        json={
            "username": "rafael",
            "email": "new@example.com",
            "password": "password123",
        },
    )
    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["detail"] == "username already exists"


def test_create_user_invalid_email_returns_422(client):
    response = client.post(
        "/users/register",
        json={
            "username": "rafael",
            "email": "invalid-email",
            "password": "password123",
        },
    )

    assert response.status_code == 422


def test_login_user_success(client):
    register_response = client.post(
        "/users/register",
        json={
            "username": "rafael",
            "email": "rafael@example.com",
            "password": "password123",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/users/login",
        json={"username": "rafael", "password": "password123"},
    )
    assert login_response.status_code == 200
    assert login_response.json()["message"] == "login successful"


def test_login_user_invalid_credentials(client):
    register_response = client.post(
        "/users/register",
        json={
            "username": "rafael",
            "email": "rafael@example.com",
            "password": "password123",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/users/login",
        json={"username": "rafael", "password": "wrong-password"},
    )
    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "invalid credentials"
