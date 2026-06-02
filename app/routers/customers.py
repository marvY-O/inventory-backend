import uuid
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.crud.customer import CustomerCRUD
from app.schemas.customer import CustomerCreate, CustomerResponse

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("", response_model=CustomerResponse, status_code=201)
async def create_customer(data: CustomerCreate, db: AsyncSession = Depends(get_db)):
    return await CustomerCRUD.create(db, data)


@router.get("", response_model=List[CustomerResponse])
async def list_customers(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await CustomerCRUD.get_all(db, skip=skip, limit=limit)


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await CustomerCRUD.get_by_id(db, customer_id)


@router.delete("/{customer_id}", status_code=204)
async def delete_customer(customer_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await CustomerCRUD.delete(db, customer_id)
