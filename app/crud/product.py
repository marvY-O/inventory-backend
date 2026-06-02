import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductCRUD:

    @staticmethod
    async def create(db: AsyncSession, data: ProductCreate) -> Product:
        existing = await db.scalar(select(Product).where(Product.sku == data.sku))
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"SKU '{data.sku}' already exists")

        product = Product(**data.model_dump())
        db.add(product)
        await db.commit()
        await db.refresh(product)
        return product

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Product]:
        result = await db.execute(select(Product).offset(skip).limit(limit))
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, product_id: uuid.UUID) -> Product:
        product = await db.scalar(select(Product).where(Product.id == product_id))
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product

    @staticmethod
    async def update(db: AsyncSession, product_id: uuid.UUID, data: ProductUpdate) -> Product:
        product = await ProductCRUD.get_by_id(db, product_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        product.updated_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(product)
        return product

    @staticmethod
    async def delete(db: AsyncSession, product_id: uuid.UUID) -> None:
        product = await ProductCRUD.get_by_id(db, product_id)
        await db.delete(product)
        await db.commit()
