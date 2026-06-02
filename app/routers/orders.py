import uuid
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.crud.order import OrderCRUD
from app.schemas.order import OrderCreate, OrderResponse

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(data: OrderCreate, db: AsyncSession = Depends(get_db)):
    return await OrderCRUD.create(db, data)


@router.get("", response_model=List[OrderResponse])
async def list_orders(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await OrderCRUD.get_all(db, skip=skip, limit=limit)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await OrderCRUD.get_by_id(db, order_id)


@router.delete("/{order_id}", status_code=204)
async def cancel_order(order_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await OrderCRUD.delete(db, order_id)
