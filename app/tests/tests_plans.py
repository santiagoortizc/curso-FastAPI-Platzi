from fastapi import status


def test_create_plan(client):
    response = client.post(
        "/plans",
        json={
            "name": "Premium Plan",
            "price": 99,
            "description": "Access to all premium features",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Premium Plan"
    assert data["price"] == 99
    assert data["description"] == "Access to all premium features"
    assert "id" in data


def test_list_plans(client):
    # Crear varios planes
    plans_data = [
        {"name": "Basic", "price": 10, "description": "Basic plan"},
        {"name": "Standard", "price": 50, "description": "Standard plan"},
        {"name": "Enterprise", "price": 200, "description": "Enterprise plan"},
    ]

    for plan in plans_data:
        response = client.post("/plans", json=plan)
        assert response.status_code == status.HTTP_201_CREATED

    # Listar todos los planes
    response = client.get("/plans")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3
    assert data[0]["name"] == "Basic"
    assert data[1]["name"] == "Standard"
    assert data[2]["name"] == "Enterprise"
