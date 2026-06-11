from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    name: str = ''
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    username: str
    name: str
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

class CustomerBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None
    vat: Optional[str] = None
    salesperson_id: Optional[str] = None
    website: Optional[str] = None

class CustomerCreate(CustomerBase):
    odoo_id: int

class CustomerOut(CustomerBase):
    id: int
    odoo_id: int

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
    sale_ok: Optional[bool] = True

class ProductCreate(ProductBase):
    odoo_id: int

class ProductOut(ProductBase):
    id: int
    odoo_id: int

    class Config:
        from_attributes = True
