import uuid
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from .. import models


class DraftRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, draft_id: uuid.UUID) -> models.QuotationDraft | None:
        return self.db.query(models.QuotationDraft).options(
            joinedload(models.QuotationDraft.lines)
        ).filter(models.QuotationDraft.id == draft_id).first()

    def list(
        self,
        customer_id: Optional[int] = None,
        status: Optional[str] = None,
        created_by: Optional[int] = None,
        q: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> list[models.QuotationDraft]:
        query = self.db.query(models.QuotationDraft).options(
            joinedload(models.QuotationDraft.lines)
        )
        if customer_id:
            query = query.filter(models.QuotationDraft.customer_id == customer_id)
        if status:
            query = query.filter(models.QuotationDraft.status == status)
        if created_by:
            query = query.filter(models.QuotationDraft.created_by == created_by)
        if q:
            query = query.filter(models.QuotationDraft.notes.ilike(f"%{q}%"))
        if date_from:
            query = query.filter(models.QuotationDraft.created_at >= date_from)
        if date_to:
            query = query.filter(models.QuotationDraft.created_at <= date_to)
        return query.order_by(models.QuotationDraft.created_at.desc()).all()

    def create(self, draft: models.QuotationDraft) -> models.QuotationDraft:
        self.db.add(draft)
        self.db.flush()
        return draft

    def save(self, draft: models.QuotationDraft):
        self.db.commit()

    def delete(self, draft: models.QuotationDraft):
        self.db.delete(draft)
        self.db.commit()
