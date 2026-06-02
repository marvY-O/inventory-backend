import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate


class CustomerCRUD:

    @staticmethod
    async def create(db: AsyncSession, data: CustomerCreate) -> Customer:
        existing = await db.scalar(select(Customer).where(Customer.email == data.email))
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Email '{data.email}' already registered")

        customer = Customer(**data.model_dump())
        db.add(customer)
        await db.commit()
        await db.refresh(customer)
        return customer

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Customer]:
        result = await db.execute(select(Customer).offset(skip).limit(limit))
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, customer_id: uuid.UUID) -> Customer:
        customer = await db.scalar(select(Customer).where(Customer.id == customer_id))
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        return customer

    @staticmethod
    async def delete(db: AsyncSession, customer_id: uuid.UUID) -> None:
        customer = await CustomerCRUD.get_by_id(db, customer_id)
        await db.delete(customer)
        await db.commit()
