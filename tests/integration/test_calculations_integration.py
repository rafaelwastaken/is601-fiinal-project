def test_calculation_bread_lifecycle(client):
    create_response = client.post(
        "/calculations",
        json={"a": 9, "b": 3, "type": "Add"},
    )
    assert create_response.status_code == 201
    created_payload = create_response.json()
    calculation_id = created_payload["id"]
    assert created_payload["result"] == 12

    browse_response = client.get("/calculations")
    assert browse_response.status_code == 200
    browse_payload = browse_response.json()
    assert len(browse_payload) == 1
    assert browse_payload[0]["id"] == calculation_id

    read_response = client.get(f"/calculations/{calculation_id}")
    assert read_response.status_code == 200
    read_payload = read_response.json()
    assert read_payload["id"] == calculation_id
    assert read_payload["result"] == 12

    update_response = client.put(
        f"/calculations/{calculation_id}",
        json={"a": 9, "b": 3, "type": "Multiply"},
    )
    assert update_response.status_code == 200
    updated_payload = update_response.json()
    assert updated_payload["id"] == calculation_id
    assert updated_payload["result"] == 27

    delete_response = client.delete(f"/calculations/{calculation_id}")
    assert delete_response.status_code == 204

    read_after_delete_response = client.get(f"/calculations/{calculation_id}")
    assert read_after_delete_response.status_code == 404
    assert read_after_delete_response.json()["detail"] == "calculation not found"


def test_create_calculation_invalid_type_returns_422(client):
    response = client.post(
        "/calculations",
        json={"a": 5, "b": 2, "type": "Modulo"},
    )

    assert response.status_code == 422


def test_create_calculation_divide_by_zero_returns_422(client):
    response = client.post(
        "/calculations",
        json={"a": 5, "b": 0, "type": "Divide"},
    )

    assert response.status_code == 422
