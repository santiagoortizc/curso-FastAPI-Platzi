from fastapi import APIRouter, HTTPException, Query, status
from db import SessionDep
from models import Customer, Transaction, TransactionCreate, TransactionWithCustomer
from sqlmodel import func, select


router = APIRouter()


@router.post(
    "/transactions", status_code=status.HTTP_201_CREATED, tags=["transactions"]
)
async def create_transaction(transaction_data: TransactionCreate, session: SessionDep):
    transaction_data_dict = transaction_data.model_dump()
    customer = session.get(Customer, transaction_data_dict.get("customer_id"))

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer doesn't exist"
        )

    transaction_db = Transaction.model_validate(transaction_data_dict)

    session.add(transaction_db)
    session.commit()
    session.refresh(transaction_db)

    return transaction_db


@router.get(
    "/transactions/{transaction_id}",
    response_model=TransactionWithCustomer,
    tags=["transactions"],
)
async def read_transaction(transaction_id: int, session: SessionDep):
    transaction = session.get(Transaction, transaction_id)
    return transaction


@router.get("/transactions")
async def list_transaction(
    session: SessionDep, skip: int = Query(0), limit: int = Query(10)
):
    total = session.exec(select(func.count(Transaction.id))).one()
    transactions = session.exec(select(Transaction).offset(skip).limit(limit)).all()

    return {"total": total, "skip": skip, "limit": limit, "data": transactions}
