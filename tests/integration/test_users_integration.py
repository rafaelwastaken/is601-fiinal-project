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


def test_get_current_user_returns_profile(client):
    register_response = client.post(
        "/register",
        json={"email": "profile@example.com", "password": "password123"},
    )
    assert register_response.status_code == 201

    headers = {"Authorization": f"Bearer {register_response.json()['access_token']}"}
    response = client.get("/users/me", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["email"] == "profile@example.com"


def test_change_password_updates_login(client):
    register_response = client.post(
        "/register",
        json={"email": "change@example.com", "password": "password123"},
    )
    assert register_response.status_code == 201

    headers = {"Authorization": f"Bearer {register_response.json()['access_token']}"}
    update_response = client.post(
        "/users/me/password",
        json={"current_password": "password123", "new_password": "newpassword123"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["message"] == "password updated"

    old_login_response = client.post(
        "/login",
        json={"email": "change@example.com", "password": "password123"},
    )
    assert old_login_response.status_code == 401

    new_login_response = client.post(
        "/login",
        json={"email": "change@example.com", "password": "newpassword123"},
    )
    assert new_login_response.status_code == 200


def test_change_password_rejects_wrong_current_password(client):
    register_response = client.post(
        "/register",
        json={"email": "wrong-current@example.com", "password": "password123"},
    )
    assert register_response.status_code == 201

    headers = {"Authorization": f"Bearer {register_response.json()['access_token']}"}
    response = client.post(
        "/users/me/password",
        json={"current_password": "badpassword", "new_password": "newpassword123"},
        headers=headers,
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "current password is incorrect"
