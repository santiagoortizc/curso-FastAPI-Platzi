from fastapi import APIRouter, status
from db import SessionDep
from models import Plan
from sqlmodel import select


router = APIRouter()


@router.post("/plans", status_code=status.HTTP_201_CREATED, tags=["plans"])
async def create_plan(plan_data: Plan, session: SessionDep):
    plan_db = Plan.model_validate(plan_data.model_dump())
    session.add(plan_db)
    session.commit()
    session.refresh(plan_db)
    return plan_db


@router.get("/plans", response_model=list[Plan], tags=["plans"])
async def list_plans(session: SessionDep):
    query = select(Plan)
    result = session.exec(query)
    return result.all()
