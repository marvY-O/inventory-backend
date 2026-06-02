import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func, text
from sqlalchemy.exc import OperationalError

from app.database import engine, Base, AsyncSessionLocal
from app.models import Product, Customer, Order  # noqa: F401 — registers models with Base
from app.routers import products, customers, orders

logger = logging.getLogger(__name__)


async def _wait_for_db(retries: int = 10, delay: float = 2.0) -> None:
    """Retry connecting to the database until it's ready."""
    for attempt in range(1, retries + 1):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("Database is ready.")
            return
        except OperationalError as exc:
            if attempt == retries:
                raise RuntimeError("Database did not become ready in time.") from exc
            logger.warning("Database not ready (attempt %d/%d), retrying in %.1fs…", attempt, retries, delay)
            await asyncio.sleep(delay)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await _wait_for_db()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Inventory & Order Management API",
    description="Production-ready REST API for managing products, customers, and orders.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(customers.router)
app.include_router(orders.router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}


@app.get("/dashboard", tags=["Dashboard"])
async def dashboard():
    async with AsyncSessionLocal() as db:
        total_products = await db.scalar(select(func.count()).select_from(Product))
        total_customers = await db.scalar(select(func.count()).select_from(Customer))
        total_orders = await db.scalar(select(func.count()).select_from(Order))

        low_stock_result = await db.execute(
            select(Product).where(Product.quantity < 10)
        )
        low_stock = low_stock_result.scalars().all()

    return {
        "total_products": total_products,
        "total_customers": total_customers,
        "total_orders": total_orders,
        "low_stock_products": [
            {"id": str(p.id), "name": p.name, "sku": p.sku, "quantity": p.quantity}
            for p in low_stock
        ],
    }
