import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    ODOO_URL: str = os.getenv("ODOO_URL")
    ODOO_DB: str = os.getenv("ODOO_DB")
    ODOO_USER: str = os.getenv("ODOO_USER")
    ODOO_PASSWORD: str = os.getenv("ODOO_PASSWORD")
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "../../.env")

settings = Settings()
