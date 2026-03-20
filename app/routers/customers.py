from fastapi import APIRouter, Query, status, HTTPException
from sqlmodel import select
from starlette.status import HTTP_404_NOT_FOUND


from models import (
    Customer,
    CustomerCreate,
    CustomerUpdate,
    CustomerWithPlans,
    Plan,
    CustomerPlan,
    StatusEnum,
)
from db import SessionDep


router = APIRouter()


@router.post(
    "/customers",
    response_model=Customer,
    status_code=status.HTTP_201_CREATED,
    tags=["costumers"],
)
async def create_customer(customer_data: CustomerCreate, session: SessionDep):
    customer = Customer.model_validate(customer_data.model_dump())
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


@router.get("/customers", response_model=list[Customer], tags=["costumers"])
async def list_customer(session: SessionDep):
    return session.exec(select(Customer)).all()


@router.get("/customers/{customer_id}", tags=["costumers"])
async def read_customer(customer_id: int, session: SessionDep):
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer doesn't exist"
        )
    return customer


@router.delete("/customers/{customer_id}", tags=["costumers"])
async def delete_customer(customer_id: int, session: SessionDep):
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer doesn't exist"
        )
    else:
        session.delete(customer)
        session.commit()
    return {"detail": "Customer deleted"}


@router.put("/customers/{customer_id}", response_model=Customer, tags=["costumers"])
async def update_customer(
    customer_id: int, customer_data: CustomerUpdate, session: SessionDep
):
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer doesn't exist"
        )
    customer_data_dict = customer_data.model_dump(exclude_unset=True)
    customer.sqlmodel_update(customer_data_dict)

    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


@router.post("/customers/{customer_id}/plans/{plan_id}")
async def suscribe_customer_plan(
    customer_id: int,
    plan_id: int,
    session: SessionDep,
    plan_status: StatusEnum = Query(),
):
    customer_db = session.get(Customer, customer_id)
    plan_db = session.get(Plan, plan_id)

    if customer_db is None or plan_db is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="The customer or plan doesn't exist"
        )

    customer_plan_db = CustomerPlan(
        customer_id=customer_db.id, plan_id=plan_db.id, status=plan_status
    )
    session.add(customer_plan_db)
    session.commit()
    session.refresh(customer_plan_db)
    return customer_plan_db


@router.get("/customers/{customer_id}/plans")
async def read_customer_plans(
    customer_id: int,
    session: SessionDep,
    plan_status: StatusEnum = Query(default=StatusEnum.ACTIVE),
):
    customer_db = session.get(Customer, customer_id)

    if customer_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    query = (
        select(CustomerPlan)
        .where(CustomerPlan.customer_id == customer_id)
        .where(CustomerPlan.status == plan_status)
    )
    plans = session.exec(query).all()

    return plans


@router.get("/customers/{customer_id}", response_model=CustomerWithPlans)
async def read_customer_with_plans(customer_id: int, session: SessionDep):
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return customer
