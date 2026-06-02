import uuid
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.crud.product import ProductCRUD
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(data: ProductCreate, db: AsyncSession = Depends(get_db)):
    return await ProductCRUD.create(db, data)


@router.get("", response_model=List[ProductResponse])
async def list_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await ProductCRUD.get_all(db, skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await ProductCRUD.get_by_id(db, product_id)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: uuid.UUID, data: ProductUpdate, db: AsyncSession = Depends(get_db)):
    return await ProductCRUD.update(db, product_id, data)


@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await ProductCRUD.delete(db, product_id)
