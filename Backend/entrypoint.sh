#!/bin/sh
set -e

echo "=== Running migrations ==="
echo "--- Stamping database at current head (tables already exist) ---"
alembic stamp head
echo "--- Applying any pending migrations ---"
alembic upgrade head

echo "=== Starting backend ==="
echo "PORT: ${PORT:-8000}"

uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
