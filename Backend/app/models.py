from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, LargeBinary, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id       = Column(Integer, primary_key=True, index=True)
    email    = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    name     = Column(String, default='')
    hashed_password = Column(String, nullable=False)
    role     = Column(String, default='vendedor')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    odoo_id = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, index=True)
    phone = Column(String)
    mobile = Column(String)
    company_name = Column(String)
    street = Column(String)
    city = Column(String)
    state = Column(String)
    zip = Column(String)
    country = Column(String)
    vat = Column(String)
    cuit = Column(String)
    vendedor_interno = Column(String)
    salesperson_id = Column(String)
    website = Column(String)


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    odoo_id = Column(Integer, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)

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
    taxes_id = Column(Text, nullable=True)
    image = Column(LargeBinary, nullable=True)

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(Integer, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    odoo_id = Column(Integer, unique=True, index=True, nullable=False)
    client_id = Column(Integer, nullable=False)
    client_name = Column(String, nullable=False)
    amount_total = Column(Float, default=0.0)
    state = Column(String, default="draft")
    date_order = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    vendedor_externo = Column(String, nullable=True)

    statuses = relationship("OrderStatus", back_populates="order", order_by="OrderStatus.changed_at.desc()")


class OrderStatus(Base):
    __tablename__ = "order_statuses"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    status = Column(String, nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    changed_by = Column(Integer, nullable=True)

    order = relationship("Order", back_populates="statuses")
