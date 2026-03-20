from fastapi import status


def test_create_customer(client):
    response = client.post(
        "/customers", json={"name": "", "email": "jhon@example.com", "age": 30}
    )
    assert response.status_code == status.HTTP_201_CREATED


def test_read_customer(client):
    response = client.post(
        "/customers", json={"name": "John Doe", "email": "jhon@example.com", "age": 30}
    )
    assert response.status_code == status.HTTP_201_CREATED
    customer_id = response.json()["id"]
    response_read = client.get(f"/customers/{customer_id}")
    assert response_read.status_code == status.HTTP_200_OK
    assert response_read.json()["name"] == "John Doe"


def test_read_customer_not_found(client):
    response = client.get("/customers/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Customer doesn't exist"


def test_list_customers(client):
    # Crear varios clientes
    customers_data = [
        {"name": "Customer 1", "email": "customer1@example.com", "age": 25},
        {"name": "Customer 2", "email": "customer2@example.com", "age": 30},
        {"name": "Customer 3", "email": "customer3@example.com", "age": 35},
    ]

    for customer in customers_data:
        response = client.post("/customers", json=customer)
        assert response.status_code == status.HTTP_201_CREATED

    # Listar todos los clientes
    response = client.get("/customers")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3


def test_delete_customer(client):
    # Crear un cliente
    response = client.post(
        "/customers",
        json={"name": "To Delete", "email": "delete@example.com", "age": 28},
    )
    assert response.status_code == status.HTTP_201_CREATED
    customer_id = response.json()["id"]

    # Eliminar el cliente
    response_delete = client.delete(f"/customers/{customer_id}")
    assert response_delete.status_code == status.HTTP_200_OK
    assert response_delete.json()["detail"] == "Customer deleted"

    # Verificar que ya no existe
    response_get = client.get(f"/customers/{customer_id}")
    assert response_get.status_code == status.HTTP_404_NOT_FOUND


def test_delete_customer_not_found(client):
    response = client.delete("/customers/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Customer doesn't exist"


def test_update_customer(client):
    # Crear un cliente
    response = client.post(
        "/customers",
        json={"name": "Original Name", "email": "update@example.com", "age": 25},
    )
    assert response.status_code == status.HTTP_201_CREATED
    customer_id = response.json()["id"]

    # Actualizar el cliente
    response_update = client.put(
        f"/customers/{customer_id}",
        json={"name": "Updated Name", "email": "update@example.com", "age": 26},
    )
    assert response_update.status_code == status.HTTP_200_OK

    # Verificar los cambios
    response_get = client.get(f"/customers/{customer_id}")
    assert response_get.status_code == status.HTTP_200_OK
    data = response_get.json()
    assert data["name"] == "Updated Name"
    assert data["age"] == 26


def test_update_customer_not_found(client):
    response = client.put(
        "/customers/9999",
        json={"name": "Test", "email": "test@example.com", "age": 30},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Customer doesn't exist"


def test_subscribe_customer_to_plan(client):
    # Crear un cliente
    customer_response = client.post(
        "/customers",
        json={"name": "Plan Customer", "email": "plan@example.com", "age": 30},
    )
    assert customer_response.status_code == status.HTTP_201_CREATED
    customer_id = customer_response.json()["id"]

    # Crear un plan
    plan_response = client.post(
        "/plans",
        json={"name": "Gold Plan", "price": 150, "description": "Premium features"},
    )
    assert plan_response.status_code == status.HTTP_201_CREATED
    plan_id = plan_response.json()["id"]

    # Suscribir el cliente al plan
    response = client.post(
        f"/customers/{customer_id}/plans/{plan_id}?plan_status=active"
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["customer_id"] == customer_id
    assert data["plan_id"] == plan_id
    assert data["status"] == "active"


def test_subscribe_customer_to_plan_not_found(client):
    # Cliente no existe
    response = client.post("/customers/9999/plans/1?plan_status=active")
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Plan no existe - crear cliente primero
    customer_response = client.post(
        "/customers",
        json={"name": "Test", "email": "testplan@example.com", "age": 25},
    )
    customer_id = customer_response.json()["id"]
    response = client.post(f"/customers/{customer_id}/plans/9999?plan_status=active")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_read_customer_plans(client):
    # Crear un cliente
    customer_response = client.post(
        "/customers",
        json={"name": "Plans Reader", "email": "plansreader@example.com", "age": 35},
    )
    customer_id = customer_response.json()["id"]

    # Crear planes
    plan1_response = client.post(
        "/plans", json={"name": "Plan A", "price": 50, "description": "Plan A desc"}
    )
    plan1_id = plan1_response.json()["id"]

    plan2_response = client.post(
        "/plans", json={"name": "Plan B", "price": 100, "description": "Plan B desc"}
    )
    plan2_id = plan2_response.json()["id"]

    # Suscribir cliente a ambos planes
    client.post(f"/customers/{customer_id}/plans/{plan1_id}?plan_status=active")
    client.post(f"/customers/{customer_id}/plans/{plan2_id}?plan_status=active")

    # Obtener planes del cliente
    response = client.get(f"/customers/{customer_id}/plans?plan_status=active")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2


def test_read_customer_plans_not_found(client):
    response = client.get("/customers/9999/plans")
    assert response.status_code == status.HTTP_404_NOT_FOUND
