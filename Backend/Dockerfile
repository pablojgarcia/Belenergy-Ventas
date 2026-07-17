FROM python:3.12-slim
WORKDIR /app
COPY Backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY Backend/app/ ./app/
COPY Backend/alembic.ini .
COPY Backend/alembic/ ./alembic/
COPY Backend/entrypoint.sh .
COPY Backend/static/ ./static/
RUN chmod +x entrypoint.sh
CMD ["/bin/sh", "entrypoint.sh"]