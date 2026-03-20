from fastapi import status


def test_create_invoice(client):
    # Primero crear un customer para usar en la factura
    customer_response = client.post(
        "/customers",
        json={"name": "Invoice Customer", "email": "invoice@example.com", "age": 40},
    )
    assert customer_response.status_code == status.HTTP_201_CREATED
    customer_data = customer_response.json()

    # Crear la factura
    invoice_data = {
        "id": 1,
        "costumer": {
            "name": customer_data["name"],
            "email": customer_data["email"],
            "age": customer_data["age"],
        },
        "transactions": [
            {
                "id": 1,
                "amount": 100,
                "description": "Service A",
                "customer_id": customer_data["id"],
            },
            {
                "id": 2,
                "amount": 200,
                "description": "Service B",
                "customer_id": customer_data["id"],
            },
        ],
        "total": 300,
    }

    response = client.post("/invoices", json=invoice_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 1
    assert data["costumer"]["name"] == "Invoice Customer"
    assert len(data["transactions"]) == 2
    assert data["total"] == 300
