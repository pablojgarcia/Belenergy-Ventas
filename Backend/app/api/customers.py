from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..repositories.customer_repository import CustomerRepository
from ..repositories.contact_repository import ContactRepository
from .. import models, schemas

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=list[schemas.CustomerOut])
def get_customers(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role == "admin":
        return CustomerRepository(db).get_all()
    return CustomerRepository(db).get_by_salesperson_ids([current_user.email, current_user.name])


@router.get("/{customer_id}", response_model=schemas.CustomerOut)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    customer = CustomerRepository(db).get_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return customer


@router.get("/{customer_id}/contacts", response_model=list[schemas.ContactOut])
def get_customer_contacts(customer_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    customer = CustomerRepository(db).get_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return ContactRepository(db).get_by_customer_id(customer_id)
