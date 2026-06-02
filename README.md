# Inventory & Order Management API

Production-ready FastAPI backend for managing products, customers, and orders.

## Tech Stack

- **Python 3.11+** / **FastAPI**
- **PostgreSQL 15** with async driver (`asyncpg`)
- **SQLAlchemy 2.0** (async ORM)
- **Alembic** for migrations
- **Pydantic v2** for request/response validation
- **Docker + Docker Compose**

## Quick Start

### 1. Configure environment

```bash
cp .env.example .env
# Edit .env with your credentials if needed
```

### 2. Run with Docker Compose

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.

### 3. View interactive docs

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Running Locally (without Docker)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Point DATABASE_URL to your local Postgres instance
export DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/inventory_db

uvicorn app.main:app --reload
```

---

## Database Migrations (Alembic)

```bash
# Generate a new migration after model changes
alembic revision --autogenerate -m "describe your change"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1
```

> **Note:** Tables are also auto-created on startup via `Base.metadata.create_all`. Use Alembic for production deployments.

---

## API Reference

### Products

| Method | Endpoint            | Description        |
|--------|---------------------|--------------------|
| POST   | `/products`         | Create a product   |
| GET    | `/products`         | List all products  |
| GET    | `/products/{id}`    | Get product by ID  |
| PUT    | `/products/{id}`    | Update a product   |
| DELETE | `/products/{id}`    | Delete a product   |

### Customers

| Method | Endpoint            | Description         |
|--------|---------------------|---------------------|
| POST   | `/customers`        | Create a customer   |
| GET    | `/customers`        | List all customers  |
| GET    | `/customers/{id}`   | Get customer by ID  |
| DELETE | `/customers/{id}`   | Delete a customer   |

### Orders

| Method | Endpoint         | Description              |
|--------|------------------|--------------------------|
| POST   | `/orders`        | Create an order          |
| GET    | `/orders`        | List all orders          |
| GET    | `/orders/{id}`   | Get order by ID          |
| DELETE | `/orders/{id}`   | Cancel/delete an order   |

### Utility

| Method | Endpoint      | Description                    |
|--------|---------------|--------------------------------|
| GET    | `/health`     | Health check                   |
| GET    | `/dashboard`  | Aggregate stats + low stock    |

### Pagination

All list endpoints support `skip` and `limit` query parameters:

```
GET /products?skip=0&limit=20
```

---

## Business Rules

1. SKU must be unique across all products.
2. Customer email must be unique.
3. Product quantity cannot go negative.
4. Orders are rejected if any product has insufficient stock.
5. On order creation: stock is deducted, `unit_price` is snapshotted, `total_amount` is auto-calculated.
6. On order cancellation: stock is restored for all order items.

---

## Error Responses

All errors return JSON:

```json
{ "detail": "error message" }
```

| Status | Meaning                         |
|--------|---------------------------------|
| 400    | Business rule violation         |
| 404    | Resource not found              |
| 422    | Request validation failed       |
# inventory-backend
