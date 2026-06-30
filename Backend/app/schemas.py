import json
import uuid
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    name: str = ''
    password: str
    role: str = 'vendedor'

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    username: str
    name: str
    role: str = 'vendedor'
    is_active: bool
    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str

class TokenData(BaseModel):
    username: str | None = None
    type: str | None = None
    jti: str | None = None

class CustomerBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    company_name: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None
    vat: Optional[str] = None
    cuit: Optional[str] = None
    vendedor_interno: Optional[str] = None
    salesperson_id: Optional[str] = None
    website: Optional[str] = None

class CustomerCreate(CustomerBase):
    odoo_id: int

class CustomerOut(CustomerBase):
    id: int
    odoo_id: int

    class Config:
        from_attributes = True


class ContactOut(BaseModel):
    id: int
    customer_id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        from_attributes = True

class TaxOut(BaseModel):
    id: int
    odoo_id: int
    name: str
    amount: float
    type_tax_use: str = "sale"

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    default_code: Optional[str] = None
    barcode: Optional[str] = None
    list_price: Optional[float] = None
    standard_price: Optional[float] = None
    type: Optional[str] = "product"
    categ_id: Optional[str] = None
    uom_id: Optional[str] = None
    description_sale: Optional[str] = None
    active: Optional[bool] = True
    taxes_id: Optional[str] = None
    taxes_display: str = ""
    taxes_rate: float = 0.0
    sale_ok: Optional[bool] = True

class ProductCreate(ProductBase):
    odoo_id: int

class ProductOut(ProductBase):
    id: int
    odoo_id: int

    class Config:
        from_attributes = True

class OrderLineInput(BaseModel):
    product_id: int
    quantity: float
    price_unit: float
    tax_id: list[int] = []
    discount: float = 0.0

class OrderCreate(BaseModel):
    partner_id: int
    order_line: list[OrderLineInput]
    description: str = ""

class OrderOut(BaseModel):
    id: int
    odoo_id: int
    client_id: int
    client_name: str
    amount_total: float
    amount_tax: float = 0.0
    state: str
    date_order: datetime
    user_id: int
    description: str | None = None
    vendedor_externo: str | None = None

    class Config:
        from_attributes = True

class OrderStatusOut(BaseModel):
    id: int
    order_id: int
    status: str
    changed_at: datetime
    changed_by: int | None = None

    class Config:
        from_attributes = True


class OrderLineOut(BaseModel):
    id: int
    order_id: int
    product_id: int
    product_name: str
    description: str | None = None
    quantity: float
    price_unit: float
    discount: float
    subtotal: float

    class Config:
        from_attributes = True


class QuotationDraftLineInput(BaseModel):
    product_id: int
    quantity: float
    unit_price: float
    discount: float = 0.0
    tax_id: list[int] = []


class QuotationDraftCreate(BaseModel):
    customer_id: int | None = None
    notes: str | None = None
    lines: list[QuotationDraftLineInput] = []


class QuotationDraftUpdate(BaseModel):
    customer_id: int | None = None
    notes: str | None = None
    lines: list[QuotationDraftLineInput] = []
    version: int


class QuotationDraftLineOut(BaseModel):
    id: uuid.UUID
    draft_id: uuid.UUID
    product_id: int
    product_odoo_id: int | None = None
    product_name: str | None = None
    quantity: float
    unit_price: float
    discount: float
    tax_id: list[int] = []
    tax_rate: float = 0.0
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("tax_id", mode="before")
    @classmethod
    def parse_tax_id(cls, v):
        if isinstance(v, str):
            return json.loads(v) if v else []
        return v or []


class QuotationDraftOut(BaseModel):
    id: uuid.UUID
    customer_id: int | None = None
    customer_name: str | None = None
    status: str = "draft"
    notes: str | None = None
    created_by: int
    updated_by: int | None = None
    created_at: datetime
    updated_at: datetime | None = None
    version: int = 1
    lines: list[QuotationDraftLineOut] = []

    model_config = {"from_attributes": True}


class QuotationOut(BaseModel):
    id: uuid.UUID
    draft_id: uuid.UUID
    customer_id: int
    customer_name: str | None = None
    amount_untaxed: float
    amount_tax: float
    amount_total: float
    odoo_sale_order_id: int
    odoo_sale_order_name: str | None = None
    lines: list[QuotationDraftLineOut] = []
    created_by: int
    created_at: datetime

    model_config = {"from_attributes": True}


class QuotationGenerateResponse(BaseModel):
    quotation_id: uuid.UUID
    odoo_sale_order_id: int
    odoo_sale_order_name: str | None = None


class LeadCreate(BaseModel):
    company_name: str
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None
    vat: Optional[str] = None
    notes: Optional[str] = None


class LeadUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None
    vat: Optional[str] = None
    notes: Optional[str] = None
    version: int


class LeadOut(BaseModel):
    id: uuid.UUID
    company_name: str
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None
    vat: Optional[str] = None
    notes: Optional[str] = None
    status: str
    rejection_reason: Optional[str] = None
    created_by: int
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    odoo_partner_id: Optional[int] = None
    odoo_crm_lead_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    version: int = 1

    model_config = {"from_attributes": True}


class LeadApprove(BaseModel):
    pass


class LeadReject(BaseModel):
    rejection_reason: str
