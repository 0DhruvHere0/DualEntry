def test_create_user(client):
    response = client.post(
        "/users/",
        json={
            "name": "Dhruv"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Dhruv"
    assert "id" in data
    assert "created_at" in data
def test_duplicate_user_name(client):
    first_response = client.post(
        "/users/",
        json={
            "name": "Dhruv"
        }
    )
    assert first_response.status_code == 201
    second_response = client.post(
        "/users/",
        json={
            "name": "Dhruv"
        }
    )
    assert second_response.status_code == 400
    assert second_response.json() == {
        "detail": "User with this name already exists"
    }