import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..services.draft_service import DraftService
from ..services.quotation_generation_service import QuotationGenerationService
from ..services.quotation_query_service import QuotationQueryService
from ..services.pdf_service import PdfService
from .. import models, schemas


# --- Drafts router ---

drafts_router = APIRouter(prefix="/quotation-drafts", tags=["quotation-drafts"])


@drafts_router.post("", response_model=schemas.QuotationDraftOut, status_code=201)
def create_draft(
    body: schemas.QuotationDraftCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    service = DraftService(db, current_user)
    return service.create(
        customer_id=body.customer_id,
        notes=body.notes,
        lines_data=[l.model_dump() for l in body.lines],
    )


@drafts_router.get("", response_model=list[schemas.QuotationDraftOut])
def list_drafts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    customer_id: int | None = Query(None),
    status: str | None = Query(None),
    q: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
):
    service = DraftService(db, current_user)
    return service.list(
        customer_id=customer_id,
        status=status,
        q=q,
        date_from=date_from,
        date_to=date_to,
    )


@drafts_router.get("/{draft_id}", response_model=schemas.QuotationDraftOut)
def get_draft(
    draft_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return DraftService(db, current_user).get(draft_id)


@drafts_router.put("/{draft_id}", response_model=schemas.QuotationDraftOut)
def update_draft(
    draft_id: uuid.UUID,
    body: schemas.QuotationDraftUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return DraftService(db, current_user).update(
        draft_id=draft_id,
        customer_id=body.customer_id,
        notes=body.notes,
        lines_data=[l.model_dump() for l in body.lines],
        version=body.version,
    )


@drafts_router.delete("/{draft_id}", status_code=204)
def delete_draft(
    draft_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    DraftService(db, current_user).delete(draft_id)


@drafts_router.post("/{draft_id}/generate", response_model=schemas.QuotationGenerateResponse)
def generate_quotation(
    draft_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    service = QuotationGenerationService(db, current_user)
    return service.generate(draft_id)


# --- Quotations router ---

quotations_router = APIRouter(prefix="/quotations", tags=["quotations"])


@quotations_router.get("", response_model=list[schemas.QuotationOut])
def list_quotations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    customer_id: int | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
):
    service = QuotationQueryService(db, current_user)
    return service.list(customer_id=customer_id, date_from=date_from, date_to=date_to)


@quotations_router.get("/{quotation_id}", response_model=schemas.QuotationOut)
def get_quotation(
    quotation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return QuotationQueryService(db, current_user).get(quotation_id)


@quotations_router.get("/{quotation_id}/pdf")
def download_pdf(
    quotation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return PdfService(db).download(quotation_id)
