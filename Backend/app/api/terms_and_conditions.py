import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user, get_current_admin
from .. import models, schemas

router = APIRouter(prefix="/terms-and-conditions", tags=["terms-and-conditions"])


@router.get("", response_model=list[schemas.TermsAndConditionsOut])
def list_terms(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.TermsAndConditions).filter(
        models.TermsAndConditions.is_active == True
    ).all()


@router.get("/{terms_id}", response_model=schemas.TermsAndConditionsOut)
def get_terms(
    terms_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    terms = db.query(models.TermsAndConditions).filter(
        models.TermsAndConditions.id == terms_id,
        models.TermsAndConditions.is_active == True,
    ).first()
    if not terms:
        raise HTTPException(status_code=404, detail="Términos no encontrados")
    return terms


@router.post("", response_model=schemas.TermsAndConditionsOut, status_code=201)
def create_terms(
    body: schemas.TermsAndConditionsCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    terms = models.TermsAndConditions(
        name=body.name,
        content=body.content,
        is_default=body.is_default,
        is_active=True,
    )
    db.add(terms)
    db.commit()
    db.refresh(terms)
    return terms


@router.put("/{terms_id}", response_model=schemas.TermsAndConditionsOut)
def update_terms(
    terms_id: uuid.UUID,
    body: schemas.TermsAndConditionsUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    terms = db.query(models.TermsAndConditions).filter(
        models.TermsAndConditions.id == terms_id
    ).first()
    if not terms:
        raise HTTPException(status_code=404, detail="Términos no encontrados")
    if body.name is not None:
        terms.name = body.name
    if body.content is not None:
        terms.content = body.content
    if body.is_default is not None:
        terms.is_default = body.is_default
    if body.is_active is not None:
        terms.is_active = body.is_active
    db.commit()
    db.refresh(terms)
    return terms


@router.delete("/{terms_id}", status_code=204)
def delete_terms(
    terms_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    terms = db.query(models.TermsAndConditions).filter(
        models.TermsAndConditions.id == terms_id
    ).first()
    if not terms:
        raise HTTPException(status_code=404, detail="Términos no encontrados")
    terms.is_active = False
    db.commit()