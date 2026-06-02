import uuid
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, ConfigDict
from app.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(..., gt=0, description="Must be greater than 0")


class OrderCreate(BaseModel):
    customer_id: uuid.UUID
    items: List[OrderItemCreate] = Field(..., min_length=1)


class OrderItemResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    unit_price: float

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    status: OrderStatus
    total_amount: float
    items: List[OrderItemResponse]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
