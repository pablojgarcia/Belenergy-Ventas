FROM python:3.12-slim
WORKDIR /app

COPY Backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Backend/app/ ./app/
COPY Backend/alembic.ini .
COPY Backend/alembic/ ./alembic/
COPY Backend/static/ ./static/

CMD exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8080}"
