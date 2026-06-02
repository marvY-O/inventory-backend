import uuid
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class CustomerBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: str = Field(..., min_length=1, max_length=50)


class CustomerCreate(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
