import uuid
from datetime import datetime, timezone
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.schemas.order import OrderCreate
from app.crud.customer import CustomerCRUD


class OrderCRUD:

    @staticmethod
    async def _load_order(db: AsyncSession, order_id: uuid.UUID) -> Order:
        """Fetch order with items and product eagerly loaded."""
        result = await db.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items).selectinload(OrderItem.product))
        )
        order = result.scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return order

    @staticmethod
    async def create(db: AsyncSession, data: OrderCreate) -> Order:
        # Verify customer exists
        await CustomerCRUD.get_by_id(db, data.customer_id)

        # Fetch all products in one query and validate stock
        product_ids = [item.product_id for item in data.items]
        result = await db.execute(select(Product).where(Product.id.in_(product_ids)))
        products_map: dict[uuid.UUID, Product] = {p.id: p for p in result.scalars().all()}

        for item in data.items:
            product = products_map.get(item.product_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product '{item.product_id}' not found",
                )
            if product.quantity < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for '{product.name}': available {product.quantity}, requested {item.quantity}",
                )

        # Build order items, deduct stock, snapshot price, calculate total
        order_items: list[OrderItem] = []
        total_amount = 0.0

        for item in data.items:
            product = products_map[item.product_id]
            product.quantity -= item.quantity
            product.updated_at = datetime.now(timezone.utc)

            unit_price = product.price
            total_amount += item.quantity * unit_price

            order_items.append(OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=unit_price,
            ))

        order = Order(
            customer_id=data.customer_id,
            status=OrderStatus.confirmed,
            total_amount=round(total_amount, 2),
            items=order_items,
        )
        db.add(order)
        await db.commit()

        return await OrderCRUD._load_order(db, order.id)

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Order]:
        result = await db.execute(
            select(Order)
            .offset(skip)
            .limit(limit)
            .options(selectinload(Order.items).selectinload(OrderItem.product))
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, order_id: uuid.UUID) -> Order:
        return await OrderCRUD._load_order(db, order_id)

    @staticmethod
    async def delete(db: AsyncSession, order_id: uuid.UUID) -> None:
        order = await OrderCRUD._load_order(db, order_id)

        if order.status == OrderStatus.cancelled:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order is already cancelled")

        # Restore stock for each item
        for item in order.items:
            item.product.quantity += item.quantity
            item.product.updated_at = datetime.now(timezone.utc)

        order.status = OrderStatus.cancelled
        order.updated_at = datetime.now(timezone.utc)
        await db.commit()
