from sqlmodel import Session

from db import engine
from models import Customer, Transaction

session = Session(engine)
customer = Customer(
    name="Santiago", description="backend developer", email="santiago@mail.com", age=22
)

session.add(customer)
session.commit()

for i in range(100):
    session.add(
        Transaction(
            amount=1000 + i, description=f"transaction {i}", customer_id=customer.id
        )
    )

session.commit()
