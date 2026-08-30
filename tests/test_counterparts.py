def test_create_counterpart(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    counterpart_response = client.post(
        "/users/",
        json={"name": "Alice"}
    )
    user_id = user_response.json()["id"]
    counterpart_id = counterpart_response.json()["id"]
    response = client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": counterpart_id,
            "relationship_type": "LENDER"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == user_id
    assert data["counterpart_id"] == counterpart_id
    assert data["counterpart_name"] == "Alice"
    assert data["relationship_type"] == "LENDER"
def test_counterpart_user_not_found(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    user_id = user_response.json()["id"]
    response = client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": 9999,
            "relationship_type": "LENDER"
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Counterpart user not found"
def test_counterpart_cannot_be_same_user(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    user_id = user_response.json()["id"]
    response = client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": user_id,
            "relationship_type": "LENDER"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == (
        "User and counterpart cannot be the same"
    )
def test_duplicate_counterpart(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    counterpart_response = client.post(
        "/users/",
        json={"name": "Alice"}
    )
    user_id = user_response.json()["id"]
    counterpart_id = counterpart_response.json()["id"]
    payload = {
        "user_id": user_id,
        "counterpart_id": counterpart_id,
        "relationship_type": "LENDER"
    }
    first_response = client.post(
        "/counterparts/",
        json=payload
    )
    assert first_response.status_code == 201
    second_response = client.post(
        "/counterparts/",
        json=payload
    )
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == (
        "Counterpart relationship already exists"
    )
def test_get_user_counterparts(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    lender_response = client.post(
        "/users/",
        json={"name": "Alice"}
    )
    borrower_response = client.post(
        "/users/",
        json={"name": "Bob"}
    )
    user_id = user_response.json()["id"]
    lender_id = lender_response.json()["id"]
    borrower_id = borrower_response.json()["id"]
    client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": lender_id,
            "relationship_type": "LENDER"
        }
    )
    client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": borrower_id,
            "relationship_type": "BORROWER"
        }
    )
    response = client.get(
        f"/counterparts/user/{user_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["counterpart_name"] in ["Alice", "Bob"]
    assert data[1]["counterpart_name"] in ["Alice", "Bob"]
def test_filter_counterparts_by_relationship_type(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    lender_response = client.post(
        "/users/",
        json={"name": "Alice"}
    )
    borrower_response = client.post(
        "/users/",
        json={"name": "Bob"}
    )
    user_id = user_response.json()["id"]
    lender_id = lender_response.json()["id"]
    borrower_id = borrower_response.json()["id"]
    client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": lender_id,
            "relationship_type": "LENDER"
        }
    )
    client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": borrower_id,
            "relationship_type": "BORROWER"
        }
    )
    response = client.get(
        f"/counterparts/user/{user_id}",
        params={"relationship_type": "LENDER"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["counterpart_name"] == "Alice"
    assert data[0]["relationship_type"] == "LENDER"