from pydantic import BaseModel, EmailStr
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
