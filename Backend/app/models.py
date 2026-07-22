import uuid
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, LargeBinary, Text, ForeignKey, Uuid
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
    odoo_id = Column(Integer, unique=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)

class Tax(Base):
    __tablename__ = "taxes"

    id = Column(Integer, primary_key=True, index=True)
    odoo_id = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    amount = Column(Float, default=0.0)
    type_tax_use = Column(String, default="sale")

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
    amount_tax = Column(Float, default=0.0)
    state = Column(String, default="draft")
    date_order = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    vendedor_externo = Column(String, nullable=True)

    lines = relationship("OrderLine", back_populates="order", order_by="OrderLine.id")
    statuses = relationship("OrderStatus", back_populates="order", order_by="OrderStatus.changed_at.desc()")


class OrderStatus(Base):
    __tablename__ = "order_statuses"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    status = Column(String, nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    changed_by = Column(Integer, nullable=True)

    order = relationship("Order", back_populates="statuses")


class OrderLine(Base):
    __tablename__ = "order_lines"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(Integer, nullable=False)
    product_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    quantity = Column(Float, default=1.0)
    price_unit = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    subtotal = Column(Float, default=0.0)

    order = relationship("Order", back_populates="lines")


class QuotationDraft(Base):
    __tablename__ = "quotation_drafts"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True, index=True)
    status = Column(String(20), default="draft", index=True)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    version = Column(Integer, default=1)

    lines = relationship("QuotationDraftLine", back_populates="draft", cascade="all, delete-orphan", order_by="QuotationDraftLine.created_at")


class QuotationDraftLine(Base):
    __tablename__ = "quotation_draft_lines"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    draft_id = Column(Uuid, ForeignKey("quotation_drafts.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product_odoo_id = Column(Integer, nullable=True)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    tax_id = Column(Text, nullable=True)
    tax_rate = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    draft = relationship("QuotationDraft", back_populates="lines")


class Quotation(Base):
    __tablename__ = "quotations"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    draft_id = Column(Uuid, ForeignKey("quotation_drafts.id"), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    amount_untaxed = Column(Float, default=0.0)
    amount_tax = Column(Float, default=0.0)
    amount_total = Column(Float, default=0.0)
    odoo_sale_order_id = Column(Integer, nullable=False)
    odoo_sale_order_name = Column(String(100), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    company_name = Column(String(255), nullable=False)
    contact_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    mobile = Column(String(50), nullable=True)
    street = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    zip = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    vat = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String(20), default="pendiente", index=True)
    rejection_reason = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    odoo_partner_id = Column(Integer, nullable=True)
    odoo_crm_lead_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    version = Column(Integer, default=1)
