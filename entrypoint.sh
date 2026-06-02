#!/bin/bash
set -e

echo "Checking for pending migrations..."
if ! alembic check; then
    echo "Pending migrations found, upgrading..."
    alembic upgrade head
else
    echo "Database is up to date, skipping migration."
fi

echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
