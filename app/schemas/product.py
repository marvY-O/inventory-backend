import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    sku: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0, description="Must be greater than 0")
    quantity: int = Field(default=0, ge=0, description="Cannot be negative")
    description: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    price: Optional[float] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None


class ProductResponse(ProductBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
