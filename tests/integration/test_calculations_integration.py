def _register_and_auth_header(client, email: str) -> dict[str, str]:
    register_response = client.post(
        "/register",
        json={"email": email, "password": "password123"},
    )
    assert register_response.status_code == 201
    token = register_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_calculation_bread_lifecycle(client):
    headers = _register_and_auth_header(client, "owner@example.com")

    create_response = client.post(
        "/calculations",
        json={"a": 9, "b": 3, "type": "Add"},
        headers=headers,
    )
    assert create_response.status_code == 201
    created_payload = create_response.json()
    calculation_id = created_payload["id"]
    assert created_payload["result"] == 12

    browse_response = client.get("/calculations", headers=headers)
    assert browse_response.status_code == 200
    browse_payload = browse_response.json()
    assert len(browse_payload) == 1
    assert browse_payload[0]["id"] == calculation_id

    read_response = client.get(f"/calculations/{calculation_id}", headers=headers)
    assert read_response.status_code == 200
    read_payload = read_response.json()
    assert read_payload["id"] == calculation_id
    assert read_payload["result"] == 12

    update_response = client.put(
        f"/calculations/{calculation_id}",
        json={"a": 9, "b": 3, "type": "Multiply"},
        headers=headers,
    )
    assert update_response.status_code == 200
    updated_payload = update_response.json()
    assert updated_payload["id"] == calculation_id
    assert updated_payload["result"] == 27

    delete_response = client.delete(f"/calculations/{calculation_id}", headers=headers)
    assert delete_response.status_code == 204

    read_after_delete_response = client.get(f"/calculations/{calculation_id}", headers=headers)
    assert read_after_delete_response.status_code == 404
    assert read_after_delete_response.json()["detail"] == "calculation not found"


def test_create_calculation_invalid_type_returns_422(client):
    headers = _register_and_auth_header(client, "typecheck@example.com")

    response = client.post(
        "/calculations",
        json={"a": 5, "b": 2, "type": "Modulo"},
        headers=headers,
    )

    assert response.status_code == 422


def test_create_calculation_divide_by_zero_returns_422(client):
    headers = _register_and_auth_header(client, "divzero@example.com")

    response = client.post(
        "/calculations",
        json={"a": 5, "b": 0, "type": "Divide"},
        headers=headers,
    )

    assert response.status_code == 422


def test_browse_requires_authentication(client):
    response = client.get("/calculations")
    assert response.status_code == 401
    assert response.json()["detail"] == "not authenticated"


def test_users_cannot_access_each_others_calculations(client):
    owner_headers = _register_and_auth_header(client, "calc-owner@example.com")
    other_headers = _register_and_auth_header(client, "calc-other@example.com")

    create_response = client.post(
        "/calculations",
        json={"a": 4, "b": 2, "type": "Multiply"},
        headers=owner_headers,
    )
    assert create_response.status_code == 201
    calc_id = create_response.json()["id"]

    owner_browse = client.get("/calculations", headers=owner_headers)
    assert owner_browse.status_code == 200
    assert len(owner_browse.json()) == 1

    other_browse = client.get("/calculations", headers=other_headers)
    assert other_browse.status_code == 200
    assert other_browse.json() == []

    other_read = client.get(f"/calculations/{calc_id}", headers=other_headers)
    assert other_read.status_code == 404

    other_delete = client.delete(f"/calculations/{calc_id}", headers=other_headers)
    assert other_delete.status_code == 404
