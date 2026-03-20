from fastapi import status


def test_create_transaction(client):
    # Primero crear un customer
    customer_response = client.post(
        "/customers",
        json={"name": "John Doe", "email": "john.transaction@example.com", "age": 30},
    )
    assert customer_response.status_code == status.HTTP_201_CREATED
    customer_id = customer_response.json()["id"]

    # Crear la transacción
    response = client.post(
        "/transactions",
        json={
            "amount": 100,
            "description": "Test transaction",
            "customer_id": customer_id,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["amount"] == 100
    assert data["description"] == "Test transaction"
    assert data["customer_id"] == customer_id


def test_create_transaction_customer_not_found(client):
    response = client.post(
        "/transactions",
        json={
            "amount": 100,
            "description": "Test transaction",
            "customer_id": 9999,
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Customer doesn't exist"


def test_read_transaction(client):
    # Crear customer
    customer_response = client.post(
        "/customers",
        json={"name": "Jane Doe", "email": "jane.transaction@example.com", "age": 25},
    )
    customer_id = customer_response.json()["id"]

    # Crear transacción
    create_response = client.post(
        "/transactions",
        json={
            "amount": 250,
            "description": "Payment for services",
            "customer_id": customer_id,
        },
    )
    transaction_id = create_response.json()["id"]

    # Leer la transacción
    response = client.get(f"/transactions/{transaction_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["amount"] == 250
    assert data["description"] == "Payment for services"
    assert data["customer"]["name"] == "Jane Doe"


def test_list_transactions(client):
    # Crear customer
    customer_response = client.post(
        "/customers",
        json={"name": "List Test", "email": "list.transaction@example.com", "age": 35},
    )
    customer_id = customer_response.json()["id"]

    # Crear varias transacciones
    for i in range(5):
        client.post(
            "/transactions",
            json={
                "amount": (i + 1) * 100,
                "description": f"Transaction {i + 1}",
                "customer_id": customer_id,
            },
        )

    # Listar transacciones con paginación
    response = client.get("/transactions?skip=0&limit=3")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 5
    assert data["skip"] == 0
    assert data["limit"] == 3
    assert len(data["data"]) == 3

    # Probar skip
    response_skip = client.get("/transactions?skip=3&limit=10")
    assert response_skip.status_code == status.HTTP_200_OK
    data_skip = response_skip.json()
    assert len(data_skip["data"]) == 2
