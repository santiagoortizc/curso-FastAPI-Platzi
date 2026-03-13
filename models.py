import email
from enum import Enum
from pydantic import BaseModel, EmailStr, field_validator
from sqlmodel import SQLModel, Field, Relationship, Session, select

from db import engine


class StatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class CustomerPlan(SQLModel, table=True):
    id: int = Field(primary_key=True)
    plan_id: int = Field(foreign_key="plan.id")
    customer_id: int = Field(foreign_key="customer.id")
    status: StatusEnum = Field(default=StatusEnum.ACTIVE)


class PlanBase(SQLModel):
    name: str
    price: int
    description: str = Field(default=None)


class PlanCreate(PlanBase):
    pass


class Plan(PlanBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    customers: list["Customer"] = Relationship(
        back_populates="plans", link_model=CustomerPlan
    )


class CustomerBase(SQLModel):
    name: str
    description: str | None = Field(default=None)
    email: EmailStr
    age: int

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        session = Session(engine)
        query = select(Customer).where(Customer.email == email)
        result = session.exec(query).first()
        if result:
            raise ValueError("This emails is alrady registered")


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):
    pass


class Customer(CustomerBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    transactions: list["Transaction"] = Relationship(back_populates="customer")
    plans: list[Plan] = Relationship(
        back_populates="customers", link_model=CustomerPlan
    )


class TransactionBase(SQLModel):
    amount: int
    description: str | None = Field(default=None)


class TransactionCreate(TransactionBase):
    customer_id: int = Field(foreign_key="customer.id")


class Transaction(TransactionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customer.id")
    customer: Customer = Relationship(back_populates="transactions")


class Invoice(BaseModel):
    id: int
    costumer: CustomerBase
    transactions: list[Transaction]
    total: int

    @property
    def amount_total(self):
        return sum(transaction.amount for transaction in self.transactions)
