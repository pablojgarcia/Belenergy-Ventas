#!/bin/sh
set -e

echo "=== Running migrations ==="
echo "--- Resetting alembic version stamp ---"
python -c "
from sqlalchemy import create_engine, text
import os
url = os.environ['DATABASE_URL']
engine = create_engine(url)
with engine.connect() as conn:
    conn.execute(text('DROP TABLE IF EXISTS alembic_version CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS contacts CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS leads CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS orders CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS products CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS refresh_tokens CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS users CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS customers CASCADE'))
    conn.commit()
print('All tables dropped')
" 2>&1 || echo "--- Could not drop tables (may not exist) ---"

for i in $(seq 1 10); do
    echo "--- Migration attempt $i/10 ---"
    alembic upgrade head && break
    echo "--- Migration failed, retrying in 2s ---"
    sleep 2
done

echo "=== Starting backend ==="
echo "PORT: ${PORT:-8000}"

uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
