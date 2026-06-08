from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, LargeBinary
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id       = Column(Integer, primary_key=True, index=True)
    email    = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    name     = Column(String, default='')
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    odoo_id = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, index=True)
    phone = Column(String)
    street = Column(String)
    city = Column(String)
    state = Column(String)
    zip = Column(String)
    country = Column(String)
    vat = Column(String)
    salesperson_id = Column(String)
    website = Column(String)

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    odoo_id = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    default_code = Column(String, index=True)
    barcode = Column(String)
    list_price = Column(Float, default=0.0)
    standard_price = Column(Float, default=0.0)
    type = Column(String, default="product")
    categ_id = Column(String)
    uom_id = Column(String)
    description_sale = Column(String)
    active = Column(Boolean, default=True)
    sale_ok = Column(Boolean, default=True)
    image = Column(LargeBinary, nullable=True)
