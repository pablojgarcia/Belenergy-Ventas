#!/bin/sh
set -e

echo "=== Running migrations ==="

for i in $(seq 1 10); do
    echo "--- Migration attempt $i/10 ---"
    alembic upgrade head && break
    echo "--- Migration failed, retrying in 2s ---"
    sleep 2
done

echo "=== Starting backend ==="
echo "PORT: ${PORT:-8000}"

uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
