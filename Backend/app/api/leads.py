import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user, get_current_admin
from ..services.lead_service import LeadService
from .. import models, schemas

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=schemas.LeadOut, status_code=201)
def create_lead(
    body: schemas.LeadCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return LeadService(db, current_user).create(body.model_dump())


@router.get("", response_model=list[schemas.LeadOut])
def list_leads(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    status: str | None = Query(None),
    q: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
):
    return LeadService(db, current_user).list(
        status=status, q=q, date_from=date_from, date_to=date_to
    )


@router.get("/{lead_id}", response_model=schemas.LeadOut)
def get_lead(
    lead_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return LeadService(db, current_user).get(lead_id)


@router.put("/{lead_id}", response_model=schemas.LeadOut)
def update_lead(
    lead_id: uuid.UUID,
    body: schemas.LeadUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return LeadService(db, current_user).update(lead_id, body.model_dump())


@router.delete("/{lead_id}", status_code=204)
def delete_lead(
    lead_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    LeadService(db, current_user).delete(lead_id)


@router.post("/{lead_id}/approve", response_model=schemas.LeadOut)
def approve_lead(
    lead_id: uuid.UUID,
    body: schemas.LeadApprove,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    return LeadService(db, current_user).approve(lead_id)


@router.post("/{lead_id}/reject", response_model=schemas.LeadOut)
def reject_lead(
    lead_id: uuid.UUID,
    body: schemas.LeadReject,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    return LeadService(db, current_user).reject(lead_id, body.rejection_reason)


@router.post("/{lead_id}/sync", response_model=schemas.LeadOut)
def sync_lead(
    lead_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return LeadService(db, current_user).sync(lead_id)


@router.post("/{lead_id}/refresh", response_model=schemas.LeadOut)
def refresh_lead(
    lead_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return LeadService(db, current_user).refresh(lead_id)


@router.post("/{lead_id}/create-partner")
def create_partner_from_lead(
    lead_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return LeadService(db, current_user).create_partner(lead_id)


@router.post("/{lead_id}/create-draft")
def create_draft_from_lead(
    lead_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return LeadService(db, current_user).create_quotation_draft(lead_id)
