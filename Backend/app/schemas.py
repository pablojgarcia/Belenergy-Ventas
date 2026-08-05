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
    seller_type: str = 'vendedor_interno'

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
    vendedor_interno: str | None = None
    seller_type: str | None = None
    model_config = {"from_attributes": True}

class UserUpdate(BaseModel):
    vendedor_interno: str | None = None
    seller_type: str | None = None

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
    new_client_name: str | None = None
    new_client_vat: str | None = None
    terms_and_conditions_id: uuid.UUID | None = None
    notes: str | None = None
    lines: list[QuotationDraftLineInput] = []


class QuotationDraftUpdate(BaseModel):
    customer_id: int | None = None
    new_client_name: str | None = None
    new_client_vat: str | None = None
    terms_and_conditions_id: uuid.UUID | None = None
    notes: str | None = None
    lines: list[QuotationDraftLineInput] = []
    version: int


class QuotationDraftLineOut(BaseModel):
    id: uuid.UUID
    draft_id: uuid.UUID
    product_id: int
    product_odoo_id: int | None = None
    product_name: str | None = None
    product_line_key: str | None = None
    quantity: float
    unit_price: float
    discount: float
    tax_id: list[int] = []
    tax_rate: float = 0.0
    discount_rule_id: uuid.UUID | None = None
    max_discount_applied: float | None = None
    seller_type_applied: str | None = None
    created_at: datetime

    @field_validator("tax_id", mode="before")
    @classmethod
    def parse_tax_id(cls, v):
        if isinstance(v, str):
            return json.loads(v) if v else []
        return v or []

    model_config = {"from_attributes": True}


class QuotationDraftOut(BaseModel):
    id: uuid.UUID
    customer_id: int | None = None
    customer_name: str | None = None
    new_client_name: str | None = None
    new_client_vat: str | None = None
    terms_and_conditions_id: uuid.UUID | None = None
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


class SyncStatusOut(BaseModel):
    status: str
    name: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    elapsed: Optional[float] = None


class TermsAndConditionsOut(BaseModel):
    id: uuid.UUID
    name: str
    content: str
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class TermsAndConditionsCreate(BaseModel):
    name: str
    content: str
    is_default: bool = False


class TermsAndConditionsUpdate(BaseModel):
    name: str | None = None
    content: str | None = None
    is_default: bool | None = None
    is_active: bool | None = None


class ProductLineOut(BaseModel):
    id: uuid.UUID
    key: str
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ProductLineCreate(BaseModel):
    key: str
    name: str


class DiscountRuleOut(BaseModel):
    id: uuid.UUID
    seller_type: str
    product_line_id: uuid.UUID | None = None
    product_line_key: str | None = None
    product_line_name: str | None = None
    condition_type: str
    min_value: float | None = None
    max_value: float | None = None
    max_discount: float
    requires_approval: bool
    is_active: bool
    created_by: int | None = None
    updated_by: int | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class DiscountRuleCreate(BaseModel):
    seller_type: str
    product_line_id: uuid.UUID | None = None
    condition_type: str
    min_value: float | None = None
    max_value: float | None = None
    max_discount: float
    requires_approval: bool = False


class DiscountRuleUpdate(BaseModel):
    seller_type: str | None = None
    product_line_id: uuid.UUID | None = None
    condition_type: str | None = None
    min_value: float | None = None
    max_value: float | None = None
    max_discount: float | None = None
    requires_approval: bool | None = None
    is_active: bool | None = None


class DiscountRuleResult(BaseModel):
    line_index: int
    product_name: str
    product_line_key: str | None = None
    max_discount: float | None = None
    requires_approval: bool = False
    tier: str | None = None
    message: str | None = None
