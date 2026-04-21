from app.security import decode_access_token


def test_register_returns_jwt_token(client):
    response = client.post(
        "/register",
        json={"email": "e2e-user@example.com", "password": "password123"},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]

    decoded = decode_access_token(payload["access_token"])
    assert decoded is not None
    assert decoded["sub"] == "e2e-user@example.com"


def test_register_duplicate_email_returns_409(client):
    body = {"email": "duplicate@example.com", "password": "password123"}
    first = client.post("/register", json=body)
    assert first.status_code == 201

    second = client.post("/register", json=body)
    assert second.status_code == 409
    assert second.json()["detail"] == "email already exists"


def test_login_returns_jwt_token_for_valid_credentials(client):
    register_response = client.post(
        "/register",
        json={"email": "login@example.com", "password": "password123"},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/login",
        json={"email": "login@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200

    payload = login_response.json()
    decoded = decode_access_token(payload["access_token"])
    assert decoded is not None
    assert decoded["sub"] == "login@example.com"


def test_login_wrong_password_returns_401(client):
    register_response = client.post(
        "/register",
        json={"email": "wrong-pass@example.com", "password": "password123"},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/login",
        json={"email": "wrong-pass@example.com", "password": "invalid123"},
    )
    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "invalid credentials"
