FROM ghcr.io/cirruslabs/flutter:stable AS flutter-build
WORKDIR /frontend
COPY Ventas/ .
RUN flutter build web --release --dart-define=SAME_ORIGIN=true

FROM python:3.12-slim
WORKDIR /app

COPY Backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Backend/app/ ./app/
COPY Backend/alembic.ini .
COPY Backend/alembic/ ./alembic/
COPY --from=flutter-build /frontend/build/web ./static/

CMD exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8080}"
