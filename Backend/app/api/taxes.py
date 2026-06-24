from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..repositories.tax_repository import TaxRepository
from .. import models, schemas

router = APIRouter(prefix="/taxes", tags=["taxes"])


@router.get("", response_model=list[schemas.TaxOut])
def get_taxes(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return TaxRepository(db).get_all()
